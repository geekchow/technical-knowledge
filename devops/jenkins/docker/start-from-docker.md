# Run jenkins master on docker

## Run a jenkins instance from docker image

```shell
# pull the jenkins image to local.
docker pull jenkins/jenkins:jdk11

# list images
docker images

# run the container
docker run -p 8080:8080 -p 50000:50000 -v ~/jenkins_home:/var/jenkins_home jenkins/jenkins:jdk11
```

## Build our own jenkins Master docker Image

```shell
# build a customised docker image
./build.sh
# run the image
./run.sh

# ls all docker containers
docker ps 

# ssh on to the docker container
docker exec -it <container name> /bin/bash

```

https://hub.docker.com/_/jenkins
https://github.com/jenkinsci/docker
https://medium.com/the-devops-ship/custom-jenkins-dockerfile-jenkins-docker-image-with-pre-installed-plugins-default-admin-user-d0107b582577