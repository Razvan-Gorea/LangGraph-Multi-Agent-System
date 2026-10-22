import os
from dotenv import load_dotenv

class Environment(object):
    def load_environment(self) -> None:
        load_dotenv()
        self.PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
        self.DEBUG_MODE = os.getenv('DEBUG_MODE') == "True"
        self.SQL_LITE_DB_STRING = os.getenv('SQL_LITE_DB_STRING')
        self.LLM_API_KEY = os.getenv('LLM_API_KEY')
        self.LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'anthropic')
        self.LLM_MODEL = os.getenv('LLM_MODEL', 'claude-sonnet-5-5')
        self.LOCAL_HOST_BACKEND_IP = os.getenv('LOCAL_HOST_BACKEND_IP')
        self.LOCAL_HOST_FRONTEND_IP = os.getenv('LOCAL_HOST_FRONTEND_IP')
        # empty MCP_SERVER_URL keeps the built-in connector tools
        self.MCP_SERVER_URL = os.getenv('MCP_SERVER_URL')
        self.MCP_AUTH_TOKEN = os.getenv('MCP_AUTH_TOKEN')
