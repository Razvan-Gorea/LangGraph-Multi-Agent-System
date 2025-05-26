import json
from colorama import Fore, Style

from application.connectors.connector_base import ConnectorBase
from application.connectors.rest_connector import RestConnector
from application.connectors.postgres_connector import PostgresConnector
from application.api.sqlclient import SQLClient
from application.api.models.connector import Connector

# this class contains the endpoints / connection strings for our data connectors.
class ConnectorBuilder():

    # create each connector here
    # basics of each defined in the sql db
    def __init__(self, sqlclient: SQLClient, pinecone_schema_path=None):
        self.connectors = {}
        self.connector_types = {
            "rest": RestConnector,
            "postgres": PostgresConnector
        }
        self.sqlclient = sqlclient
        self.initial_load_connectors()
 
    def set_integration_agent(self, integration_agent):
        self.integration_agent = integration_agent

    def load_from_file(self, config_file_path):
        with open(config_file_path, "r") as file:
            return json.load(file)
 
    def initial_load_connectors(self):
        data = self.sqlclient.get_all_records(Connector)

        for connector_config in data:
            connector_type = connector_config.type_c   
            name = connector_config.name
            
            if connector_type not in self.connector_types:
                raise Exception(f"Unknown connector type: {connector_type}")
            
            # dynamically load in connectors, no schema needed
            connector_class = self.connector_types[connector_type]
            self.connectors[name] = connector_class(connector_config)
             
    def get_connector(self, name):
        return self.connectors.get(name)
    
    def list_connectors(self):
        return list(self.connectors.keys())

    def add_new_connector(self, connector):
        """
        Adds a new connector and starts it up.
        """
        if connector.type_c not in self.connector_types:
            raise Exception(f"Unknown connector type: {connector.type_c}")
        
        connector_class = self.connector_types[connector.type_c]
        self.connectors[connector.name] = connector_class(connector)

    def list_all_specific_type_connector(self, filter_attr, filter_value):
        filtered_connectors = []
        for name, connector in self.connectors.items():
            if hasattr(connector, filter_attr):
                # Get the attribute value and compare
                attr_value = getattr(connector, filter_attr)
                if attr_value == filter_value:
                    filtered_connectors.append(connector)
        return filtered_connectors

    def startup_all_connectors(self):
        """
            Go to each connector and run its startup method.
            Connector types that dont need startup just do nothing here.
        """

        for connector in self.connectors.values():
            self.startup_connector(connector)

    def startup_connector(self, connector: ConnectorBase):
        print(Fore.GREEN + "INFO" + Style.RESET_ALL + f":     {connector.name} starting up...")
        try:
            connector.startup(self.integration_agent)
        except Exception as e:
            print(Fore.RED + "ERROR" + Style.RESET_ALL + f":    [{connector.name}] {e}")
    def shutdown_all_connectors(self):
        """
            Go to each connector and run its shutdown method.
            Connector types with no shutdown will do nothing
        """

        for connector in self.connectors.values():
            if connector.active:
                print(Fore.GREEN + "INFO" + Style.RESET_ALL + f":     {connector.name} shutting_down...")
                connector.shutdown()
