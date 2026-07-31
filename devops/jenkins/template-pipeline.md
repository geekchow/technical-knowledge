# how make template pipeline

## why we need template pipeline?

> Image such scenario, your team developed a large quantity of iOS librares repositories. Each repository need to create a pipeline to do PR checking, lib release etc. How can you manage those pipelines? create pipeline for each repository, each repository has the same Jenkinsfile? That's bad smell. As a coder, you'd better never repeat yourself. That's why a template pipeline comes along.

## How template pipeline works?

> We use the `pipeline-multiple-defaults-plugins` to 




## Reference
https://github.com/jenkinsci/config-file-provider-plugin
  > It will allow you to copy various similar configuration files to all your nodes.

https://github.com/jenkinsci/pipeline-multibranch-defaults-plugin  
  > Configuration files will be referenced from the global Jenkins script store provided by the config-file provider plugin. If a multibranch pipeline is configured to use a default Jenkinsfile, then the following happens:
    >  - Every branch discovered is assumed to have a Jenkinsfile because of the default Jenkinsfile setting.
    >  - Every pull request discovered is assumed to have a Jenkinsfile because of the default Jenkinsfile setting.
    >  - When discover tags is enabled, every tag is assumed to have a Jenkinsfile because of the default Jenkinsfile setting.