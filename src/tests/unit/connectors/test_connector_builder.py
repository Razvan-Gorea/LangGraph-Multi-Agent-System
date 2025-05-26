from application.api.sqlclient import SQLClient
from tests.conftest import get_test_rest_connector
from application.connectors.connector_builder import ConnectorBuilder
from application.connectors.rest_connector import RestConnector
import pytest

def test_initial_load_connectors_success(sqlclient: SQLClient):
    connector = get_test_rest_connector()
    sqlclient.add_object(connector)

    connector_builder = ConnectorBuilder(sqlclient)

    assert connector.name in connector_builder.connectors
    assert isinstance(connector_builder.connectors[connector.name], RestConnector)

def test_initial_load_connectors_connector_type_not_supported(sqlclient: SQLClient):
    connector = get_test_rest_connector()
    connector.type_c = "rats"
    sqlclient.add_object(connector)

    with pytest.raises(Exception, match="Unknown connector type: rats"):
        connector_builder = ConnectorBuilder(sqlclient)
        assert connector.name not in connector_builder.connectors

def test_get_connector_success(sqlclient: SQLClient):
    connector = get_test_rest_connector()
    sqlclient.add_object(connector)

    connector_builder = ConnectorBuilder(sqlclient)

    new_connector = connector_builder.get_connector(connector.name)

    assert new_connector is not None
    assert new_connector.name == connector.name

def test_get_connector_not_found(sqlclient: SQLClient):
    connector_builder = ConnectorBuilder(sqlclient)

    new_connector = connector_builder.get_connector("hello")

    assert new_connector is None

def test_list_connectors_empty_list(sqlclient: SQLClient):
    connector_builder = ConnectorBuilder(sqlclient)
    
    connectors = connector_builder.list_connectors()

    assert len(connectors) == 0

def test_list_connectors_with_items(sqlclient: SQLClient):
    connector = get_test_rest_connector()
    sqlclient.add_object(connector)
    connector_builder = ConnectorBuilder(sqlclient)

    connectors = connector_builder.list_connectors()
    assert len(connectors) == 1
    assert connectors[0] == connector.name

def test_add_new_connector_success(sqlclient: SQLClient):
    connector = get_test_rest_connector()
    connector_builder = ConnectorBuilder(sqlclient)

    connector_builder.add_new_connector(connector)
    new_connector = connector_builder.get_connector(connector.name)

    assert new_connector is not None
    assert new_connector.name == connector.name

def test_add_new_connector_exception(sqlclient: SQLClient):
    connector = get_test_rest_connector()
    connector.type_c = "rats"
    connector_builder = ConnectorBuilder(sqlclient)

    with pytest.raises(Exception, match="Unknown connector type: rats"):
        connector_builder.add_new_connector(connector)
        assert len(connector_builder.connectors) == 0

def test_list_all_specific_type_connector(sqlclient: SQLClient):
    connector = get_test_rest_connector()
    sqlclient.add_object(connector)
    connector_builder = ConnectorBuilder(sqlclient)

    connectors = connector_builder.list_all_specific_type_connector("type_c", "rest")
    
    assert len(connectors) == 1
    assert connectors[0].type_c == "rest"

def test_startup_connector_success(sqlclient: SQLClient):
    connector = get_test_rest_connector()
    other_connector = get_test_rest_connector()
    other_connector.name = "goodbye"
    other_connector.id = 2

    sqlclient.bulk_add_object([connector, other_connector])
    connector_builder = ConnectorBuilder(sqlclient)
    connector_builder.integration_agent = None
    base_connector = connector_builder.connectors[connector.name]

    connector_builder.startup_connector(base_connector)

    assert connector_builder.connectors[connector.name].active == True


