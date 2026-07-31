docker run -d \
	--name phil-postgres \
	-e POSTGRES_PASSWORD=mysecretpassword \
	-e PGDATA=/var/lib/postgresql/data/pgdata \
	-v /home/phil/postgres/data:/var/lib/postgresql/data \
    -p 8080:8080 \
	postgres