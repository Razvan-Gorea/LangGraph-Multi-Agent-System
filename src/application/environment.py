import os
from dotenv import load_dotenv

class Environment(object):
    def load_environment(self) -> None:
        load_dotenv()
        self.PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
        self.DEBUG_MODE = os.getenv('DEBUG_MODE') == "True"
        self.SQL_LITE_DB_STRING = os.getenv('SQL_LITE_DB_STRING')
        self.DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
        self.LOCAL_HOST_BACKEND_IP = os.getenv('LOCAL_HOST_BACKEND_IP')
        self.LOCAL_HOST_FRONTEND_IP = os.getenv('LOCAL_HOST_FRONTEND_IP')
