import requests
import json
from requests.exceptions import RequestException
from application.api.models.connector import Connector
from application.connectors.connector_base import ConnectorBase

class RestConnector(ConnectorBase):
    def __init__(self, config: Connector):
        
        super().__init__(config)
        self.base_url = config.c_params["base_url"]
        self.headers = config.c_params["headers"]
        self.timeout = config.c_params["timeout"]
        self.retries = config.c_params["retries"]
        self.schema = ""
        
        if config.c_params["has_schema"] == "True":
            self.schema = self.load_schema()

        if "api_key" in config.c_params.keys():
            self.api_key = config.c_params["api_key"]
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    def load_schema(self):
        schema = f"application/seeds/connectors/spec_{self.name}.json"
        with open(schema, "r") as file:
            return json.load(file)

    # dirty method for making http req, use the below nicer methods as tools instead.
    def request_handler(self, method, endpoint, params=None, data=None):
        url = f"{self.base_url}{endpoint}"
        headers = self.headers

        # loop on our retries
        for attempt in range(self.retries):
            # for once i need try catch
            try:
                response = requests.request(
                    method,
                    url,
                    params=params,
                    json=data,
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except RequestException as e:
                if attempt == self.retries - 1:
                    raise Exception(f"Request failed after {self.retries} attempts. {e}")
                continue
    
    def load_metadata(self):
        return self.schema

    # proper methods for use by the agent
    def get(self, endpoint, params=None):
        return self.request_handler("GET", endpoint, params=params)
    
    def post(self, endpoint, data=None):
        return self.request_handler("POST", endpoint, data=data)
    
    def put(self, endpoint, data=None):
        return self.request_handler("PUT", endpoint, data=data)
    
    def delete(self, endpoint):
        return self.request_handler("DELETE", endpoint)
