import json

from fastapi.testclient import TestClient
from application.api.sqlclient import SQLClient
from application.api.models.user import User
from application.api.models.permission import Permission
from tests.conftest import get_test_user, get_test_user_json, get_test_permission, get_test_permission_json

# get_user_by_id
def test_get_user_by_id_unprocessable(client: TestClient):
    response = client.get("user/blah")
    
    assert response.status_code == 422
    assert response.text == '{"detail":[{"type":"int_parsing","loc":["path","user_id"],"msg":"Input should be a valid integer, unable to parse string as an integer","input":"blah"}]}' 

def test_get_user_by_id_not_found(client: TestClient):
    response = client.get("user/1")
    
    assert response.status_code == 404
    assert response.text == '{"detail":"User not found"}'

def test_get_user_by_id_success(client: TestClient, sqlclient: SQLClient):
    user = get_test_user()
    
    sqlclient.add_object(user)
    response = client.get("user/1")
    
    content = json.loads(response.text)

    assert response.status_code == 200
    assert content["id"] == 1
    assert content["username"] == "hello"
    assert content["email"] == "hello@"
    assert content["is_admin"] == False
    assert content["permissions"] == []

# login
def test_login_not_found(client: TestClient):
    user = get_test_user_json()
    response = client.post(url="user/login", json=user)

    assert response.status_code == 404
    assert response.text == '{"detail":"User not found"}'

def test_login_success(client: TestClient, sqlclient: SQLClient):
    user = get_test_user()
    sqlclient.add_object(user)

    response = client.post(url="user/login", json=get_test_user_json())
    content = json.loads(response.text)

    assert response.status_code == 200
    assert content["id"] == 1

# create_user
def test_create_user_success(client: TestClient):
    user = get_test_user_json()
    response = client.post(url="user/create", json=user)
    content = json.loads(response.text)

    assert response.status_code == 200
    assert content["id"] == user["id"]
    assert content["username"] == user["username"]
    assert content["email"] == user["email"]
    assert content["password"] != user["password"]

# replace user
def test_replace_user_not_found(client: TestClient):
    new_user = get_test_user_json()

    response = client.put("user/2", json=new_user)

    assert response.status_code == 404
    assert response.text == '{"detail":"User not found"}'

def test_replace_user_success(client: TestClient, sqlclient: SQLClient):
    old_user = User(
        id=2,
        username="goodbye",
        email="goodbye@",
        password="rats",
        is_admin=False
    )
    sqlclient.add_object(old_user)

    new_user = get_test_user_json()
    

    response = client.put("user/2", json=new_user)
    content = json.loads(response.text)

    assert response.status_code == 200
    assert content["id"] == 1
    assert content["username"] == "hello"
    assert content["email"] == "hello@"

# delete_user
def test_delete_user_not_found(client: TestClient):
    response = client.delete("user/1")

    assert response.status_code == 404
    assert response.text == '{"detail":"User not found"}'

def test_delete_user_success(client: TestClient, sqlclient: SQLClient):
    sqlclient.add_object(get_test_user())

    response = client.delete("user/1")

    assert response.status_code == 200
    assert response.text == '{"message":"User deleted"}'

# get_permission
def test_get_permission_not_found(client: TestClient):
   response = client.get("permission/1")

   assert response.status_code == 404
   assert response.text == '{"detail":"Permission not found"}'

def test_get_permission_success(client: TestClient, sqlclient: SQLClient):
    sqlclient.add_object(get_test_permission())
    permission = get_test_permission_json()

    response = client.get("permission/1")
    content = json.loads(response.text)

    assert response.status_code == 200
    assert content["id"] == permission["id"]
    assert content["permission_name"] == permission["permission_name"]

# create_permission
def test_create_permission_success(client: TestClient):
    permission = get_test_permission_json()
    response = client.post("permission/create", json=permission)
    content = json.loads(response.text)

    assert response.status_code == 200
    assert content["id"] == permission["id"]
    assert content["permission_name"] == permission["permission_name"]

# update_permission
def test_update_permission_not_found(client: TestClient):
    permission = get_test_permission_json()
    response = client.put("permission/1", json=permission)

    assert response.status_code == 404
    assert response.text == '{"detail":"Permission not found"}'

def test_update_permission_success(client: TestClient, sqlclient: SQLClient):
    old_permission = Permission(
        id=2,
        permission_name="old"
    )
    sqlclient.add_object(old_permission)

    permission = get_test_permission_json()
    response = client.put("permission/2", json=permission)
    content = json.loads(response.text)

    assert response.status_code == 200
    assert content["id"] == permission["id"]
    assert content["permission_name"] == permission["permission_name"]

# delete_permission
def test_delete_permission_not_found(client: TestClient):
    response = client.delete("permission/1")

    assert response.status_code == 404
    assert response.text == '{"detail":"Permission not found"}'

def test_delete_permission_success(client: TestClient, sqlclient: SQLClient):
    permission = get_test_permission()
    sqlclient.add_object(permission)

    response = client.delete("permission/1")

    assert response.status_code == 200
    assert response.text == '{"message":"Permission deleted"}'
