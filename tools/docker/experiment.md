
```shell
# pull ubuntu:trusty
docker pull ubuntu:trusty

# create a new container with image: ubuntu:trusty
docker run -dti \
	--name phil-ubuntu \
	ubuntu:trusty

# ssh on to running container
docker exec -it phil-ubuntu bash
```