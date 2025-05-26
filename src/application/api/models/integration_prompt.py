from pydantic import BaseModel

class IntegrationPrompt(BaseModel):
    connector_name: str
    connector_type: str
    connector_schema: str
    body: str

    def to_string(self):
        return ("This is connector name: "+ self.connector_name + 
                ". This is the connector type: "+ self.connector_type + 
                ". This is the connector schema: " + str(self.connector_schema) +
                ". This is the user query:" + self.body
        )
