from psycopg2.extras import DictCursor
from confluent_kafka import Consumer
import psycopg2
import json
import requests
import threading

from application.api.models.connector import Connector
from application.connectors.connector_base import ConnectorBase

class PostgresConnector(ConnectorBase):
    def __init__(self, config: Connector):

        super().__init__(config)
        self.connection_params = {
            "dbname": config.c_params["db_name"],
            "user": config.c_params["user"],
            "password": config.c_params["password"],
            "host": config.c_params["host"],
            "port": config.c_params["port"],
        }

        self.event_config = {
            "name": config.name,
            "config": {
                "connector.class": config.e_params["class"], 
                "database.hostname": config.c_params["host"], 
                "database.port": config.c_params["port"], 
                "database.user": config.c_params["user"], 
                "database.password": config.c_params["password"], 
                "database.dbname" : config.c_params["db_name"], 
                "topic.prefix": config.e_params["topic"], 
                "table.include.list": config.e_params["include_list"],
                "plugin.name": config.e_params["plugin.name"],
                "publication.name": config.e_params["publication.name"]
            }
        }

        self.monitor_thread = None
        self.stop_monitoring = False

    def execute_sql_query(self, query):
        cursor = self.connection.cursor(cursor_factory=DictCursor)
        cursor.execute(query)
        self.connection.commit()

        if cursor.description:
            return cursor.fetchall()

    def load_metadata(self):
        return self.execute_sql_query("select * from information_schema.tables where table_schema='public'")

    def debezium_connector(self):
        config_json = json.dumps(self.event_config)

        get_connectors = requests.get(f'http://connect:8083/connectors/{self.event_config["name"]}')

        if get_connectors.status_code == 200:
            requests.delete(f'http://connect:8083/connectors/{self.event_config["name"]}')
            response = requests.post(
            "http://connect:8083/connectors/",
            data=config_json,
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )

        else:
            response = requests.post(
            "http://connect:8083/connectors/",
            data=config_json,
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )

        result = response.json
        return result
    
    def start_monitoring(self, integration_agent=None, kafka_bootstrap_servers='kafka:9092'):    
        # Changing if a thread already exists and is alive
        if self.monitor_thread and self.monitor_thread.is_alive():
            return
            
        self.stop_monitoring = False
        self.monitor_thread = threading.Thread(
            target=self._monitor_events,
            args=(integration_agent, kafka_bootstrap_servers),
            daemon=True
        )

        self.monitor_thread.start()
        return self.monitor_thread
        
    def stop_monitoring_events(self):
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.stop_monitoring = True # Flag to used to stop thread
            self.monitor_thread.join(timeout=5)

    def _monitor_events(self, integration_agent=None, kafka_bootstrap_servers='kafka:9092'):
        # Kafka consumer config
        conf = {
            'bootstrap.servers': kafka_bootstrap_servers,
            'group.id': 'database-change-monitor',
            'auto.offset.reset': 'latest',
            'enable.auto.commit': True
        }
        
        topic_prefix = self.event_config['config']['topic.prefix']
        
        admin_consumer = Consumer(conf)
        
        cluster_metadata = admin_consumer.list_topics(timeout=10)
        
        matching_topics = [topic for topic in cluster_metadata.topics.keys() 
                            if topic.startswith(f"{topic_prefix}.")]
        
        admin_consumer.close()
        
        if not matching_topics:
            return
        
        consumer = Consumer(conf)
        
        # Subscribe consumer to all matching topics
        consumer.subscribe(matching_topics)
        
        while not self.stop_monitoring:
            msg = consumer.poll(1.0)
                
            if msg is None:
                continue
                    
            if msg.error() or msg.value() is None:
                continue
            
            # Useful for potentially debugging
            # Maybe we should implement verification check for event???
            # event = json.loads(msg.value().decode('utf-8'))
                    
            # Get the payload which contains the actual data
            # payload = event.get('payload', {})

            # Get timestamps
            # source_ts_ms = payload.get('source', {}).get('ts_ms')
                    
            # Get table information
            # source_schema = payload.get('source', {}).get('schema')
            # source_table = payload.get('source', {}).get('table')
                
            # Timestamp
            # source_datetime = datetime.fromtimestamp(source_ts_ms/1000).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                    
            # Operation type
            # operation = payload.get('op')
                    
            # print(f"\n--- Database Change Detected for {self.name} ---")
            # print(f"Schema: {source_schema}")
            # print(f"Table: {source_table}")
            # print(f"Operation: {operation}")
            # print(f"Occurred at: {source_datetime}")
            
            # Process data if integration_agent is provided
            
            if integration_agent:
                # Re-run the same ingestion process that runs on startup
                integration_agent.graph.invoke({
                    "messages": [
                        {"role": "user", "content": "This is the name of the connector: " + self.event_config["name"] + ", " + "this is the type of connector: " + self.type_c + ", " + "This is the schema: " + str(self.load_metadata())},
                    ],
                    "data_store": self.event_config["name"]
                })
        consumer.close()

    def startup(self, integration_agent):
        self.connection = psycopg2.connect(**self.connection_params)
        self.debezium_connector()
        self.start_monitoring(integration_agent)
        self.active = True
