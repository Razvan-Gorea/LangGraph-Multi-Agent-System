from application.api.models.connector import Connector
# child inits should not do anything failure prone (like listening) in their inits

class ConnectorBase():
    def __init__(self, config: Connector):
        self.type_c = config.type_c
        self.name = config.name
        self.active = False
    
    # startup logic in children should replace this (If you have any)
    def startup(self, integration_agent):
        self.active = True

    # shutdown logic in children should replace this (If you have any)
    def shutdown(self):
        pass
