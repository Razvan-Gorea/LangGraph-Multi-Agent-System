# Define Variables
CONTAINER_NAME=postgres_container
IMAGE_NAME=postgres:alpine
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=mydatabase
PORT=5432

# Pull the apline PostgresSQL container
pull:
	@echo "Pulling Alpine PostgresSQL image"
	docker pull postgres:alpine

# Start the PostgreSQL container
build_and_run:
	@echo "Building and running PostgreSQL container"
	docker run --name $(CONTAINER_NAME) \
		-e POSTGRES_USER=$(POSTGRES_USER) \
		-e POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) \
		-e POSTGRES_DB=$(POSTGRES_DB) \
		-p $(PORT):5432 -d $(IMAGE_NAME)

build:
	@echo "Building PostgreSQL image"
	docker build -t $(IMAGE_NAME) .

start:
	@echo "Booting up the container"
	docker start postgres_container

populate:
	@echo "Populating the database"
	docker exec -i postgres_container psql -U myuser -d mydatabase < dummy_data.sql

# Stop the PostgreSQL container
stop:
	@echo "Stopping PostgreSQL container"
	docker stop $(CONTAINER_NAME)

# Remove the PostgreSQL container
remove:
	@echo "PostgreSQL container removed"
	docker rm $(CONTAINER_NAME)

# Remove the PostgreSQL image
remove-image:
	@echo "Removing PostgreSQL image"
	docker rmi $(IMAGE_NAME)

# Show PostgreSQL logs
logs:
	@echo "Showing logs of the PostgreSQL container"
	docker logs $(CONTAINER_NAME)

# Connect to the PostgreSQL container using psql
connect:
	@echo "Opening interactive session inside the PostgresSQL container"
	docker exec -it $(CONTAINER_NAME) psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

# Following data needs to be added in the postgresql.conf file in order for debezium connector to capture changes

# wal_level = logical (remove comment symbol in file)
# max_wal_senders = 10 (remove comment symbol in file)
# max_replication_slots = 10 (remove comment symbol in file)

# Run `docker exec -it postgres_container bash`
# Then run `vi /var/lib/postgresql/data/postgresql.conf`
# Then search for the relevant lines, comment and edit them in
