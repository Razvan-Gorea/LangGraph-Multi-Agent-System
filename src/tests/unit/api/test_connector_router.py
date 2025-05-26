import json
from fastapi.testclient import TestClient

from application.api.sqlclient import SQLClient
from tests.conftest import get_test_rest_connector, get_test_rest_connector_json

# get_all_connectors
def test_get_all_connectors_success_no_records(client: TestClient):
   response = client.get("connector/all")

   assert response.text == '[]'
   assert response.status_code == 200

def test_get_all_connectors_success_records(client: TestClient, sqlclient: SQLClient):
    sqlclient.add_object(get_test_rest_connector())

    response = client.get("connector/all")
    content = json.loads(response.text)
    connector_json = get_test_rest_connector_json()

    assert response.status_code == 200
    assert content[0]["id"] == connector_json["id"]
    assert content[0]["name"] == connector_json["name"]
    assert content[0]["type_c"] == connector_json["type_c"]
    assert content[0]["c_params"] == connector_json["c_params"]
    assert content[0]["e_params"] == connector_json["e_params"]

# get_connector
def test_get_connector_not_found(client: TestClient):
    response = client.get("connector/hello")

    assert response.status_code == 404
    assert response.text == '{"detail":"Connector not Found"}'

# create_connector
def test_create_connector_success(client: TestClient):
    connector = get_test_rest_connector_json()
    response = client.post(url="connector/new", json=connector)
    response_json = response.json()

    assert response.status_code == 200
    assert response_json["id"] == connector["id"]
    assert response_json["name"] == connector["name"]
    assert response_json["type_c"] == connector["type_c"]
    assert response_json["c_params"] == connector["c_params"]
    assert response_json["e_params"] == connector["e_params"]
