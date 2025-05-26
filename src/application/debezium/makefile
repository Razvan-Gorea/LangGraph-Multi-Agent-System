# Run ZooKeeper container
zookeeper:
	docker run -it --rm --name zookeeper -p 2181:2181 -p 2888:2888 -p 3888:3888 quay.io/debezium/zookeeper:3.0

# Run Kafka container
kafka:
	docker run -it --rm --name kafka -p 9092:9092 --link zookeeper:zookeeper quay.io/debezium/kafka:3.0

# Have postgres client running before running this command
kafka-connect:
	docker run -it --rm --name connect -p 8083:8083 -e GROUP_ID=1 -e CONFIG_STORAGE_TOPIC=my_connect_configs -e OFFSET_STORAGE_TOPIC=my_connect_offsets -e STATUS_STORAGE_TOPIC=my_connect_statuses --link kafka:kafka --link postgres_container:postgres_container quay.io/debezium/connect:3.0

# Run Zookeeper, then kafka, then postgres (apply the relevent postgres.conf changes then restart the container), then kafka-connect, then main.py

# If main.py is already running, restart it after running kafka connect
