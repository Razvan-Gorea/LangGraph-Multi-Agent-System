from application.dbutils import DbUtils
from application.agents.tools.query_dbutils import create_pinecone_tool
from application.agents.tools.namespace_tool import namespace_tool
from application.agents.tools.query_connectors import create_connector_tool
from application.agents.tools.upsert_dbutils import create_upserter_tool

from langchain_core.tools import BaseTool
from unittest.mock import MagicMock

def test_query_dbutils_tool(dbutils: DbUtils):
    mock_dbutils = MagicMock()
    mock_dbutils.create_query_embedding.return_value = [0.1, 0.2, 0.3]
    mock_dbutils.search.return_value = [{"id": "1", "score": "0.9"}, {"id": "2", "score": "0.8"}]

    pinecone_tool = create_pinecone_tool(mock_dbutils)
    
    result = pinecone_tool.run(tool_input={"user_query":"test query", "namespace":"test_namespace"}) 

    assert result == [{"id": "1", "score": "0.9"}, {"id": "2", "score": "0.8"}]
    assert isinstance(pinecone_tool, BaseTool)

def test_namespace_tool(dbutils: DbUtils):
    mock_dbutils = MagicMock()
    mock_dbutils.get_namespaces.return_value = ["namespace1", "namespace2"]

    tool = namespace_tool(mock_dbutils)

    result = tool.run(tool_input={})

    assert result == ["namespace1", "namespace2"]
    assert isinstance(tool, BaseTool)

def test_query_rest_connector_tool():
    mock_connector_builder = MagicMock()
    mock_rest_connector = MagicMock()

    mock_connector_builder.get_connector.return_value = mock_rest_connector
    mock_rest_connector.get.return_value = {"data": "rest_response"}

    tool = create_connector_tool(mock_connector_builder)[1]

    rest_input = {
        "connector_name": "rest_connector",
        "endpoint": "/api/data",
        "params": {"param1", "param2"}
    }

    result = tool.run(tool_input=rest_input)

    assert result == {"data": "rest_response"}

    assert isinstance(tool, BaseTool)

def test_query_postgres_connector():
    mock_connector_builder = MagicMock()
    mock_postgres_connector = MagicMock()

    mock_connector_builder.get_connector.return_value = mock_postgres_connector
    mock_postgres_connector.execute_sql_query.return_value = [{"id": 1, "name": "test"}]

    tool = create_connector_tool(mock_connector_builder)[0]

    postgres_input = {
        "connector_name": "postgres_connector",
        "query": "select * from table"
    }

    result = tool.run(tool_input=postgres_input)

    assert result == [{"id": 1, "name": "test"}]
    assert isinstance(tool, BaseTool)

def test_upsert_dbutils():
    mock_dbutils = MagicMock()

    mock_dbutils.create_embedding.return_value = [{"values": [0.1, 0.2, 0.3]}, {"values": [0.4, 0.5, 0.6]}]
    mock_dbutils.upsert_embeddings.return_value = 2

    upsert_tool = create_upserter_tool(mock_dbutils)

    test_data = [
        {"id": "1", "text": "hello"},
        {"id": "1", "text": "goodbye"}
    ]
    
    tool_input = {
        "data": test_data,
        "namespace": "test_namespace"
    }

    result = upsert_tool.run(tool_input=tool_input)

    assert result == 2
    assert isinstance(upsert_tool, BaseTool)
