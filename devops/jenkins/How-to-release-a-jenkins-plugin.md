# How to release a Jenkins Plugin to Jenkins-CI artifactory?

If you want to host your Jenkins Plugins on to Jenkins-CI offical artifactory, you have to go through the follow steps.

- 1. Host your source code under Jenkins-CI github organization.

    - 1. Host your plugin [source code](https://github.com/geekchow/secure-post-script-plugin) under your own github account.
      
    - 2. Raise a hosting [request](https://issues.jenkins-ci.org/projects/HOSTING/issues/HOSTING-1016?filter=allissues) on Jenkins-JIRA.
      - Firstly, you have to register an account on Jenkins-JIRA.
      - Then, create a new issue in the [hosting project](https://issues.jenkins-ci.org/browse/HOSTING)
      - Waiting for jenkins team to review your source code, it takes weeks to complete. 
      - Finally, your plugin is approved, your source code will be forked to [jenkins-ci organization](https://github.com/jenkinsci), and meanwhile you're invited to the `jenkinsci` team.

- 2. Apply Jenkins-CI artifactory write permission.
    - 1. Logon to the Jenkins-CI artifactory, with the account applied in step 1.2.(*Caution: Do logon once before do release*)
    - 2. Raise a PR to https://github.com/jenkins-infra/repository-permissions-updater/#requesting-permissions to get release permission.
      > pick up any closed PR for example, the pr usually approved within hours. 

- 3. Release your plugin to Jenkins-CI artifactory.
    - 1. Prepare maven distribution server configuration
      
      - 1. Configure distribution server in the `pom.xml` file.
      
        ```xml
        <distributionManagement>
          <repository>
              <id>releases</id>
              <url>https://repo.jenkins-ci.org/releases</url>
          </repository>
          <snapshotRepository>
              <id>snapshots</id>
              <url>https://repo.jenkins-ci.org/snapshots</url>
          </snapshotRepository>
        </distributionManagement>
        ```
      - 2. Configure credential of distribution servers in maven global settings (~/.m2/settings.xml).
        > retrieve your encrypted password from [Jenkins Artifactory](https://repo.jenkins-ci.org/webapp/#/profile).
        ```xml
        <servers>
          <server>
          <server>
            <id>releases</id>
            <username>username...</username>
            <password>pwd....</password>
          </server>
          <server>
            <id>snapshots</id>
            <username>username...</username>
            <password>pwd....</password>
          </server>
        </servers>
        ```
        > Caution: You'd better verify if the configuration takes effect.
        ```bash
        mvn help:effective-settings
        # verify if the output is intented to your expectation. 
        ```
    
    - 2. Release the plugin.
      
      release a snapshot version to verify.
      ```bash
      mvn deploy
      # release to https://repo.jenkins-ci.org/snapshots/io/jenkins/plugins
      ```

      release a formal release version.
      ```bash
      mvn release:prepare release:perform
      # release to https://repo.jenkins-ci.org/releases/io/jenkins/plugins/
      ```

      The source code will be scanned by SpotBugs while releasing, ususally you'll get the [error message](https://stackoverflow.com/questions/12242291/what-is-the-meaning-of-possible-null-pointer-dereference-in-findbug): `NP: Possible null pointer dereference (NP_NULL_ON_SOME_PATH)`.  If you don't have experience, it will confuse you a lot. 
      
      origin code get error:
      ```java
      ...
      if (run.getResult().isWorseThan(SecurePostScriptConfiguration.get().getResultCondition())) {
        return;
      }
      ...
      ```

      modified code still get error
      ```java
      ...
      if (run.getResult() != null && run.getResult().isWorseThan(SecurePostScriptConfiguration.get().getResultCondition())) {
        return;
      }
      ...
      ```
      Why I already checked `run.getResult()` is not null, before call `isWorseThan()`?
      That's because, no none could garantee that the first `run.getResult()` return the same value as the second call.

      final workable code without error.
      ```java
      ...
      Result result = run.getResult();
      if (result != null) {
        if ( result.isWorseThan(SecurePostScriptConfiguration.get().getResultCondition())) {
          return;
        }
      }
      ...
      ```


      









## References
https://www.jenkins.io/doc/developer/publishing/requesting-hosting/