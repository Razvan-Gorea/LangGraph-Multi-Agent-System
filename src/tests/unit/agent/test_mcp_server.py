import asyncio
import json
import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from application.mcp_server import create_mcp_server, BearerAuth

def make_builder():
    rest = MagicMock(type_c="rest")
    rest.get.return_value = {"day": "Monday"}
    pg = MagicMock(type_c="postgres")
    pg.execute_sql_query.return_value = [{"id": 1}]
    builder = MagicMock()
    builder.get_connector.side_effect = {"r": rest, "p": pg}.get
    return builder

def call(mcp, tool, args):
    content, _ = asyncio.run(mcp.call_tool(tool, args))
    return json.loads(content[0].text)

def test_tools_listed():
    names = {t.name for t in asyncio.run(create_mcp_server(make_builder()).list_tools())}
    assert names == {"query_rest_connector", "query_postgres_connector"}

def test_rest_and_postgres_tools():
    mcp = create_mcp_server(make_builder())
    assert call(mcp, "query_rest_connector", {"connector_name": "r", "endpoint": "/day"}) == {"day": "Monday"}
    assert call(mcp, "query_postgres_connector", {"connector_name": "p", "query": "select 1"}) == [{"id": 1}]

def test_wrong_connector_type_is_rejected():
    mcp = create_mcp_server(make_builder())
    with pytest.raises(Exception, match="No postgres connector named 'r'"):
        call(mcp, "query_postgres_connector", {"connector_name": "r", "query": "select 1"})

def test_bearer_auth():
    inner = FastAPI()
    inner.get("/")(lambda: "ok")
    client = TestClient(BearerAuth(inner, "tok"))
    assert client.get("/").status_code == 401
    assert client.get("/", headers={"Authorization": "Bearer nope"}).status_code == 401
    assert client.get("/", headers={"Authorization": "Bearer tok"}).status_code == 200
