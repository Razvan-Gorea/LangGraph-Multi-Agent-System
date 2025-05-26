from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder

from application.api.sqlclient import SQLClient
from application.api.models.user import User
from tests.conftest import create_test_conversation, create_test_chat

# get_last_conversation
def test_get_last_conversation_not_found(client: TestClient):
    response = client.post("/conversation/latest?user_id=1")
    assert response.status_code == 200
    assert response.json() is None

def test_get_last_conversation_success(client: TestClient, sqlclient: SQLClient):
    convo1 = create_test_conversation(user_id=1, id=1)
    convo2 = create_test_conversation(user_id=1, id=2)
    convo3 = create_test_conversation(user_id=1, id=3)
    sqlclient.add_object(convo1)
    sqlclient.add_object(convo2)
    sqlclient.add_object(convo3)

    response = client.post("/conversation/latest?user_id=1")
    content = response.json()

    assert response.status_code == 200
    assert content["id"] == 3

# get_all_conversations
def test_get_all_conversations_empty(client: TestClient):
    response = client.post("/conversation/all?user_id=1")

    assert response.status_code == 200
    assert response.json() == []

def test_get_all_conversations_success(client: TestClient, sqlclient: SQLClient):
    convo1 = create_test_conversation(user_id=1, id=1)
    convo2 = create_test_conversation(user_id=1, id=2)
    convo3 = create_test_conversation(user_id=2, id=3) # other user
    sqlclient.add_object(convo1)
    sqlclient.add_object(convo2)
    sqlclient.add_object(convo3)

    response = client.post("/conversation/all?user_id=1")
    content = response.json()

    assert response.status_code == 200
    assert len(content) == 2
    assert content[0]["id"] in [1, 2]
    assert content[1]["id"] in [1, 2]
    assert content[0]["user_id"] == 1
    assert content[1]["user_id"] == 1

# get_conversation
def test_get_conversation_not_found(client: TestClient):
    response = client.get("/conversation/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Conversation not found"}

def test_get_conversation_success(client: TestClient, sqlclient: SQLClient):
    conversation = create_test_conversation(id=1)
    sqlclient.add_object(conversation)
    response = client.get("/conversation/1")
    content = response.json()

    assert response.status_code == 200
    assert content["id"] == 1
    assert content["title"] == "Test Conversation"

# create_conversation
def test_create_conversation_success(client: TestClient):
    conversation = create_test_conversation(id=10)
    response = client.post("/conversation/create", json=jsonable_encoder(conversation))
    content = response.json()
    
    assert response.status_code == 200
    assert content["id"] == 10
    assert content["title"] == "Test Conversation"

# update_conversation
def test_update_conversation_not_found(client: TestClient):
    conversation = create_test_conversation(id=1)
    response = client.put("/conversation/1", json=jsonable_encoder(conversation))

    assert response.status_code == 404
    assert response.json() == {"detail": "Conversation not found"}

def test_update_conversation_success(client: TestClient, sqlclient: SQLClient):
    old_conversation = create_test_conversation(id=1, title="Old Name")
    sqlclient.add_object(old_conversation)
    new_conversation = create_test_conversation(id=1, title="New Name")
    
    response = client.put("/conversation/1", json=jsonable_encoder(new_conversation))
    content = response.json()

    assert response.status_code == 200
    assert content["id"] == 1
    assert content["title"] == "New Name"

# delete_conversation
def test_delete_conversation_not_found(client: TestClient):
    response = client.delete("/conversation/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Conversation not found"}

def test_delete_conversation_success(client: TestClient, sqlclient: SQLClient):
    conversation = create_test_conversation(id=1)
    sqlclient.add_object(conversation)
    response = client.delete("/conversation/1")

    assert response.status_code == 200
    assert response.json() == {"message": "Conversation deleted"}

# get_all_chats_in_conversation
def test_get_all_chats_in_conversation_empty(client: TestClient):
    response = client.get("/conversation/1/chat/all")

    assert response.status_code == 200
    assert response.json() == []

def test_get_all_chats_in_conversation_success(client: TestClient, sqlclient: SQLClient):
    chat1 = create_test_chat(conversation_id=1, id=1, body="Chat 1")
    chat2 = create_test_chat(conversation_id=1, id=2, body="Chat 2")
    chat3 = create_test_chat(conversation_id=2, id=3, body="Chat 3")
    sqlclient.add_object(chat1)
    sqlclient.add_object(chat2)
    sqlclient.add_object(chat3)
    
    response = client.get("/conversation/1/chat/all")
    content = response.json()

    assert response.status_code == 200
    assert len(content) == 2
    assert content[0]["id"] in [1, 2]
    assert content[1]["id"] in [1, 2]
    assert content[0]["body"] in ["Chat 1", "Chat 2"]
    assert content[1]["body"] in ["Chat 1", "Chat 2"]

# get_chat
def test_get_chat_not_found(client: TestClient):
    response = client.get("/conversation/1/chat/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Chat not found"}

def test_get_chat_success(client: TestClient, sqlclient: SQLClient):
    chat = create_test_chat(conversation_id=1, id=1, body="Test Chat")
    sqlclient.add_object(chat)
    response = client.get("/conversation/1/chat/1")
    content = response.json()

    assert response.status_code == 200
    assert content["id"] == 1
    assert content["body"] == "Test Chat"

# create_chat
def test_create_chat_success(client: TestClient, sqlclient: SQLClient):
    conversation = create_test_conversation(id=1)
    sqlclient.add_object(conversation)
    user = User(id=1, username="testuser", email="test@example.com", password="password", is_admin=False)
    sqlclient.add_object(user)

    chat = create_test_chat(conversation_id=1, body="User Input")
    
    response = client.post("/conversation/1/chat/create", json=jsonable_encoder(chat))
    content = response.json()

    assert response.status_code == 200
    assert content["body"] == "User Input"
    assert content["conversation_id"] == 1

# generate response
def test_create_response_success(client: TestClient, sqlclient):
    conversation = create_test_conversation(id=1)
    sqlclient.add_object(conversation)
    user = User(id=1, username="testuser", email="test@example.com", password="password", is_admin=False)
    sqlclient.add_object(user)

    chat = create_test_chat(conversation_id=1, body="User Input")
    response = client.post("/conversation/1/chat/response", json=jsonable_encoder(chat))
    content = response.json()

    assert response.status_code == 200
    assert content["conversation_id"] == 1


# delete_chat
def test_delete_chat_not_found(client: TestClient):
    response = client.delete("/conversation/1/chat/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Chat not found"}

def test_delete_chat_success(client: TestClient, sqlclient: SQLClient):
    chat = create_test_chat(conversation_id=1, id=1)
    sqlclient.add_object(chat)
    response = client.delete("/conversation/1/chat/1")

    assert response.status_code == 200
    assert response.json() == {"message": "Chat deleted"}

# update_chat
def test_update_chat_not_found(client: TestClient):
    chat = create_test_chat(conversation_id=1, id=1)
    response = client.put("/conversation/1/chat/1", json=jsonable_encoder(chat))

    assert response.status_code == 404
    assert response.json() == {"detail": "Chat not found"}

def test_update_chat_success(client: TestClient, sqlclient: SQLClient):
    old_chat = create_test_chat(conversation_id=1, id=1, body="Old Chat Text")
    sqlclient.add_object(old_chat)
    new_chat = create_test_chat(conversation_id=1, id=1, body="New Chat Text")
    response = client.put("/conversation/1/chat/1", json=jsonable_encoder(new_chat))
    content = response.json()

    assert response.status_code == 200
    assert content["id"] == 1
    assert content["body"] == "New Chat Text"
