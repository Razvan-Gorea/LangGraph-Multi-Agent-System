import pytest
from typing import Any
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import MagicMock, patch
from langchain_core.messages import HumanMessage
from langchain_mistralai import ChatMistralAI

from main import app
from application.environment import Environment
from application.api.sqlclient import SQLClient 
from application.dbutils import DbUtils
from application.api.dependencies import get_sql_client, get_dbutils, get_supervisor_agent
from application.agents.tools.query_dbutils import create_pinecone_tool
from application.agents.supervisor_agent.supervisor_agent import SupervisorAgent
from application.api.models.permission import Permission
from application.api.models.user import User
from application.api.models.connector import Connector
from application.api.models.conversation import Conversation
from application.api.models.chat import Chat

class MockAgent():
    def take_input(self, input_message: str, permissions: str):
        return "Mock Agent Response"

@pytest.fixture(name='environment')
def environment_fixture() -> Environment:
    env = Environment()
    env.load_environment()
    return env

@pytest.fixture(name='connect_args')
def connect_args_fixture() -> dict[str, bool]:
    return {'check_same_thread': False}

@pytest.fixture(name='sqlclient')
def sqlclient_fixture(environment: Environment, connect_args: dict[str, bool]):
    environment.SQL_LITE_DB_STRING = "sqlite:///test.db"
    sqlclient = SQLClient(environment, connect_args)
    sqlclient.create_db_and_tables()
    yield sqlclient
    sqlclient.drop_all_tables()

@pytest.fixture(name='dbutils')
def dbutils_fixture(environment: Environment):
    dbutils = DbUtils(environment, 96, 200, "multilingual-e5-large")
    yield dbutils

@pytest.fixture(name='client')
def client_fixture(sqlclient: SQLClient, dbutils: DbUtils): 
    def get_db_override():
        yield sqlclient

    def get_dbutils_override():
        yield dbutils

    def get_supervisor_agent_override():
        mock_agent = MockAgent()
        yield mock_agent

    app.dependency_overrides[get_sql_client] =  get_db_override
    app.dependency_overrides[get_dbutils] = get_dbutils_override
    app.dependency_overrides[get_supervisor_agent] = get_supervisor_agent_override


    client = TestClient(app)
    yield client

# testing for agents
@pytest.fixture
def mock_env():
    mock = MagicMock()
    mock.DEEPSEEK_API_KEY = "test_api_key"
    return mock

@pytest.fixture
def mock_dbutils():
    return MagicMock(spec=DbUtils)

@pytest.fixture
def mock_pinecone_tool():
    return MagicMock()

@pytest.fixture
def supervisor_agent(mock_env, mock_dbutils, mock_pinecone_tool):
    create_pinecone_tool.return_value = mock_pinecone_tool
    return SupervisorAgent(mock_env, mock_dbutils)

@pytest.fixture
def initial_state():
    return {"messages": [HumanMessage(content="Test Query")]}

@pytest.fixture
def mock_chat_mistralai():
    with patch.object(ChatMistralAI, "invoke") as mock:
        yield mock

@pytest.fixture
def mock_chat_mistralai_structured():
    with patch.object(ChatMistralAI, "with_structured_output") as mock:
        yield mock

# test data

def get_test_user() -> User:
    return User(
        id=1, 
        username="hello", 
        email="hello@", 
        password="Qvbe", 
        is_admin=False
    )

def get_test_user_json() -> dict[str, Any]:
    return {
        "id": 1,
        "username": "hello",
        "email": "hello@",
        "password": "Qvbe",
        "is_admin": False
    }

def get_test_permission() -> Permission:
    return Permission(
        id=1, 
        permission_name="test"
    )

def get_test_permission_json() -> dict[str, Any]:
    return{
        "id": 1,
        "permission_name": "test"
    }

def get_test_rest_connector() -> Connector:
    return Connector(
        id=1,
        name="hello",
        type_c="rest",
        c_params = {
            "base_url": "hello",
            "timeout": 1,
            "headers": "hello",
            "retries": 1,
            "has_schema": False
        },
        e_params = {"test_e": "goodbye"}
    )

def get_test_rest_connector_json() -> dict[str, Any]:
    return {
        "id": 1,
        "name": "hello",
        "type_c": "rest",
        "c_params": {
            "base_url": "hello",
            "headers": "hello",
            "timeout": 1,
            "retries": 1,
            "has_schema": False
        },
        "e_params": {"test_e": "goodbye"}
    }

def get_test_conversation() -> Conversation:
    return Conversation(
        id=1,
        user_id=1,
        title="Test Conversation",
        last_modified_date=datetime.utcnow(),
    )

def get_test_chat() -> Chat:
    return Chat(
        id=1,
        conversation_id=1,
        body="test",
        last_modified_date=datetime.utcnow(),
    )

# helpers
def create_test_conversation(user_id: int = 1, id: int = 1, title:str = "Test Conversation") -> Conversation:
    return Conversation(
        id=id,
        user_id=user_id,
        title=title,
        last_modified_date=datetime.utcnow(),
    )


def create_test_chat(conversation_id: int = 1, id: int = 1, body: str = "Test Chat Message") -> Chat:
    return Chat(
        id=id,
        conversation_id=conversation_id,
        body=body,
        last_modified_date=datetime.utcnow(),
    )
