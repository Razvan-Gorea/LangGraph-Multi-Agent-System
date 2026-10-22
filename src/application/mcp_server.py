import asyncio
import hmac
import json

from mcp.server.fastmcp import FastMCP
from starlette.responses import Response


def create_mcp_server(connector_builder) -> FastMCP:
    """
    MCP server over the live connectors. To expose a new datastore, add one @mcp.tool() here.
    """
    mcp = FastMCP("docgenie-connectors", streamable_http_path="/")

    def find(name: str, type_c: str):
        connector = connector_builder.get_connector(name)
        if connector is None or connector.type_c != type_c:
            raise ValueError(f"No {type_c} connector named '{name}'")
        return connector

    # connector calls block (requests, psycopg2), so keep them off the event loop
    @mcp.tool()
    async def query_rest_connector(connector_name: str, endpoint: str, params: dict | None = None) -> str:
        """
        This tool takes an endpoint and parameters and hits that endpoint.
        It gives you back the response.
        """
        res = await asyncio.to_thread(find(connector_name, "rest").get, endpoint, params)
        return json.dumps(res, default=str)

    @mcp.tool()
    async def query_postgres_connector(connector_name: str, query: str) -> str:
        """
        This tool takes your SQL query and executes it, returning the response.
        The connector_name parameter is just the name of the connector you want to connect to.
        """
        rows = await asyncio.to_thread(find(connector_name, "postgres").execute_sql_query, query)
        return json.dumps([dict(r) for r in rows or []], default=str)

    return mcp


class BearerAuth:
    """ASGI middleware: 401 unless the request carries the shared bearer token."""

    def __init__(self, app, token: str):
        self.app = app
        self.expected = f"Bearer {token}".encode()

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            given = dict(scope["headers"]).get(b"authorization", b"")
            if not hmac.compare_digest(given, self.expected):
                return await Response(status_code=401)(scope, receive, send)
        await self.app(scope, receive, send)
