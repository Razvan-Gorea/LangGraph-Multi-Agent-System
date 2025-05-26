from fastapi.testclient import TestClient

def test_seed_users_db(client: TestClient):
    response = client.get('/seed/user')
    assert response.status_code == 200
    assert response.text == '"ok"'

def test_seed_permission_db(client: TestClient):
    response = client.get('/seed/permission')
    assert response.status_code == 200
    assert response.text == '"ok"'

def test_seed_conversations_db(client: TestClient):
    response = client.get('/seed/conversation')
    assert response.status_code == 200
    assert response.text == '"ok"'

def test_seed_connector_db(client: TestClient):
    response = client.get('/seed/connector')
    assert response.status_code == 200
    assert response.text == '"ok"'

def test_seed_all_db(client: TestClient):
    response = client.get('seed/all')
    assert response.status_code == 200
    assert response.text == '"ok"'

