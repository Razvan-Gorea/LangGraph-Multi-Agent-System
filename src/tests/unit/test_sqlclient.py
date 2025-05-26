import pytest
import bcrypt
from sqlmodel import Session
from application.api.sqlclient import SQLClient
from application.environment import Environment
from time import sleep
from application.api.models.user import User
from application.api.models.chat import Chat
from application.api.models.conversation import Conversation

# Creating a mock of the environment 
@pytest.fixture
def mock_environment(monkeypatch):
    # TODO MOCK ENV LIKE A NORMAL OBJECT, THIS IS NOT GOOD
    monkeypatch.setenv('PINECONE_API_KEY', 'mock_pinecone_key')
    monkeypatch.setenv('DEBUG_MODE', 'True')
    monkeypatch.setenv('SQL_LITE_DB_STRING', 'sqlite:///test.db')
    monkeypatch.setenv('DEEPSEEK_API_KEY', 'mock_anthropic_key')
    monkeypatch.setenv('LOCAL_HOST_BACKEND_IP', '127.0.0.1')
    monkeypatch.setenv('LOCAL_HOST_FRONTEND_IP', 'http://localhost:3000')
   
    mock_env = Environment()
    mock_env.load_environment()
    return mock_env
   
@pytest.fixture
def mock_connect_args():
    return {"check_same_thread": False}

@pytest.fixture()
def mock_client(mock_environment, mock_connect_args):
    client = SQLClient(env=mock_environment, connect_args=mock_connect_args)
    client.create_db_and_tables()
    yield client
    
    # Clean up the test.db after each unit test
    client.drop_all_tables()
    
@pytest.fixture
def mock_session(mock_client):
    session = Session(mock_client.engine)
    yield session

def test_get_session(mock_session):
    assert mock_session is not None

def test_hash_password(mock_client):
    """Testing if hash_password method works"""
    password = "1234567890"
    mock_password = mock_client.hash_password(password)

    assert isinstance(mock_password, str)
    assert mock_password != password
    assert mock_password != ""

def test_compare_hash(mock_client):
    """Testing if compare_hash method works"""
    password = "1234567890"
    mock_hash = mock_client.hash_password(password)
    bcrypt_check = bcrypt.checkpw(password.encode('utf-8'), mock_hash.encode('utf-8'))
    assert mock_client.compare_hash(password, mock_hash) is True
    assert mock_client.compare_hash(password, mock_hash) == bcrypt_check
    assert mock_client.compare_hash("wrong_password", mock_hash) is False
    
        
def test_add_object(mock_client):
    """Testing if add_object method works"""
    test_add_user = mock_client.add_object(User(username = "test", email = "test@example.com", password = "1234567890"))
    retrieved = mock_client.get_by_id(User, test_add_user.id)
    
    assert test_add_user == retrieved
    assert retrieved is not None
    assert retrieved.id == test_add_user.id
    assert retrieved.username == test_add_user.username
    assert retrieved.email == test_add_user.email
    assert retrieved.password == test_add_user.password

def test_bulk_add_object(mock_client):
    """Test if a bulk_add_object method works"""
    user_1 = User(username= "user_1", email="user1@example.com", password="user1password")
    user_2 = User(username="user2", email="user2@example.com", password="user2password")
    users = [user_1,user_2]
    
    mock_client.bulk_add_object(users)

    retrieved_user_1 = mock_client.get_by_id(User, user_1.id)
    retrieved_user_2 = mock_client.get_by_id(User, user_2.id)
    
    assert retrieved_user_1 is not None
    assert retrieved_user_2 is not None
    assert retrieved_user_1 != retrieved_user_2
    
    assert retrieved_user_1.username == user_1.username 
    assert retrieved_user_1.email == user_1.email
    assert retrieved_user_1.password == user_1.password
    assert retrieved_user_1.id == user_1.id

    assert retrieved_user_2.username == user_2.username 
    assert retrieved_user_2.email == user_2.email
    assert retrieved_user_2.password == user_2.password
    assert retrieved_user_2.id == user_2.id

def test_replace_object(mock_client):
    """Testing if the replace_object method works"""
    original_user = User(username="original_user", email="original_user@example.com", password="1234567890")
    current_entry = mock_client.add_object(original_user)

    test_retrieval = mock_client.get_by_id(User, current_entry.id)
    assert test_retrieval is not None

    original_username = original_user.username
    original_email = original_user.email
    original_password = original_user.password

    new_user = User(id=current_entry.id, username="new_user", email="new_user@example.com", password="0987654321")
    new_entry = mock_client.replace_object(current_entry, new_user)

    assert new_entry is not None
    assert original_username != new_entry.username
    assert original_email != new_entry.email
    assert original_password != new_entry.password

    assert current_entry.id == new_entry.id

    assert new_entry.username == "new_user"
    assert new_entry.email == "new_user@example.com"
    assert new_entry.password == "0987654321"

def test_delete_object(mock_client):
    """Testing if the delete_object method works"""
    sample_user = User(username="sample_user", email="sample_user@example.com", password="1234567890")
    adding_user = mock_client.add_object(sample_user)

    assert adding_user is not None
    assert adding_user.id is not None

    retrieve = mock_client.get_by_id(User, adding_user.id)

    assert retrieve is not None
    assert retrieve.email == "sample_user@example.com"
    assert retrieve.username == "sample_user"
    assert retrieve.password is not None

    second_retrieve = mock_client.delete_object(retrieve)
    assert second_retrieve is None

    deleted_user = mock_client.get_by_id(User, adding_user.id)
    assert deleted_user is None

def test_get_by_id(mock_client):
    """Testing if the get_by_id method"""    
    test_user = User(username="test_user", email="test_user@example.com", password="1234567890")
    submission = mock_client.add_object(test_user)

    assert submission is not None
    assert submission.id is not None

    user_retrieval = mock_client.get_by_id(User, submission.id)

    assert user_retrieval is not None
    assert type(user_retrieval) == type(test_user)
    assert user_retrieval.id == submission.id
    assert user_retrieval.username == test_user.username
    assert user_retrieval.email == test_user.email

    # Testing false id that doesn't exist
    false_id = 100000000000000
    false_test = mock_client.get_by_id(User, false_id)

    assert false_test is None

def test_get_by_email(mock_client):
    """Testing if the get_by_id method"""    
    email_test = User(username="hello_user", email="some_test_user@example.com", password="1234567890")
    submission = mock_client.add_object(email_test)

    assert submission is not None
    assert submission.id is not None

    tester = mock_client.get_by_email(User, submission.email)

    assert tester.id == submission.id
    assert tester.email == submission.email
    assert tester.username == submission.username
    
    # False Test

    false_email = "none_existent_email@email.com"

    tmp = mock_client.get_by_email(User, false_email)
    assert tmp is None
    mock_client.delete_object(submission)

def test_get_latest_conversation(mock_client):
    """Testing the get_latest_conversation"""
    test_user = User(username="test_user12345", email="test_user12345@email.com", password="1234567890")
    testing_user = mock_client.add_object(test_user)

    conversation_object_1 = Conversation(title="first conversation", user_id=testing_user.id)
    first_conversation = mock_client.add_object(conversation_object_1)

    sleep(2)

    conversation_object_2 = Conversation(title="second conversation", user_id=testing_user.id)
    second_conversation = mock_client.add_object(conversation_object_2)

    latest_conversation = mock_client.get_latest_conversation(testing_user.id)

    assert latest_conversation == second_conversation
    assert latest_conversation != first_conversation
    assert latest_conversation.id == second_conversation.id
    assert latest_conversation.title == "second conversation"
    assert latest_conversation.title == second_conversation.title
    assert latest_conversation.last_modified_date == second_conversation.last_modified_date
    assert latest_conversation.user_id == testing_user.id

    # False test

    test_user_2 = User(username="test_user67890", email="test_user67890@email.com", password="1234567890")
    testing_user_2 = mock_client.add_object(test_user_2)
    false_conversation = mock_client.get_latest_conversation(testing_user_2.id)

    assert false_conversation is None

def test_get_by_column(mock_client):
    """Testing the get_by_column method"""
    column_test_user = User(username="column_test_user", email="column_test_user@email.com", password="1234567890")
    object_added = mock_client.add_object(column_test_user)

    testing_by_column = mock_client.get_by_column(User, "email", "column_test_user@email.com")

    assert len(testing_by_column) == 1
    assert testing_by_column[0].id == object_added.id

    mock_client.delete_object(object_added)
    false_test = mock_client.get_by_column(User, "body", "body_type")

    assert false_test is None

    column_test_user = User(username="column_test_user", email="column_test_user@email.com", password="1234567890")
    object_added = mock_client.add_object(column_test_user)

    testing_by_column = mock_client.get_by_column(User, "email", "column_test_user@email.com")

    special_test = mock_client.get_by_column(User, "email", "this_email_shouldn't_exist@email.com")

    assert len(special_test) == 0
    assert type(special_test) == list

    mock_client.delete_object(object_added)
