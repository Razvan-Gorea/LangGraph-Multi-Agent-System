import os
import subprocess
import uvicorn

from contextlib import asynccontextmanager, AsyncExitStack
from colorama import just_fix_windows_console
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware 

from config import env, sqlclient, connector_manager, integration_agent
from application.api.models.integration_prompt import IntegrationPrompt
from application.mcp_server import create_mcp_server, BearerAuth

from application.api.routes.user_routes import userRouter
from application.api.routes.chat_routes import chatRouter
from application.api.routes.seed_routes import seedRouter
from application.api.routes.connector_routes import connectorRouter

# startup event
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncExitStack() as stack:
        if mcp:
            await stack.enter_async_context(mcp.session_manager.run())
        connector_manager.set_integration_agent(integration_agent)
        connector_manager.startup_all_connectors()
        yield
        # shutdown events
        # shutdown all the connectors (if needed)
        connector_manager.shutdown_all_connectors()

# the MCP server runs inside this app so it shares the live connectors (their DB connections come from startup)
mcp = create_mcp_server(connector_manager) if env.MCP_SERVER_URL else None

app = FastAPI(lifespan=lifespan)

if mcp:
    # it exposes raw SQL and port 8888 is published, so never mount it without a token
    if not env.MCP_AUTH_TOKEN:
        raise RuntimeError("MCP_SERVER_URL is set but MCP_AUTH_TOKEN is empty")
    app.mount("/mcp", BearerAuth(mcp.streamable_http_app(), env.MCP_AUTH_TOKEN))

@app.post("/receive_webhook/{connector_name}")
async def receive_webhook(connector_name:str, request: Request):
    reqbody = await request.json()
    print(reqbody)
    connector = connector_manager.get_connector(connector_name)
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
   
    prompt = IntegrationPrompt(
        connector_name=connector.name,
        connector_type = connector.type_c,
        connector_schema = str(connector.schema),
        body = str(reqbody)
    )
    await integration_agent.graph.ainvoke({
        "messages": [
            {"role": "user", "content": prompt.to_string()},
        ],
        "data_store": connector_name
    })
    return {"message": "Webhook received"}

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.include_router(userRouter)
app.include_router(chatRouter)
app.include_router(seedRouter)
app.include_router(connectorRouter)

if __name__ == "__main__":
    # colorama for windows
    just_fix_windows_console()

    # spawns a subprocess for next
    # TODO this needs to be cleaned up, and using more env vars
    next_dir = os.path.join("application", "front_end", "docgenie")
    os.chdir(next_dir)
    
    if os.name == 'nt':
        npm_path = "npm.cmd"
    else:
        npm_path = "npm"

    command=[npm_path, "run", "dev"]
    next_env = None
    if os.environ.get("FRONTEND_STANDALONE"):
        # Docker image ships the built standalone server, no npm; it must bind 0.0.0.0 to be reachable
        command = ["node", "server.js"]
        next_env = {**os.environ, "HOSTNAME": "0.0.0.0", "PORT": "3000"}

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=next_env)
    os.chdir("../../..")
    uvicorn.run(app, host=env.LOCAL_HOST_BACKEND_IP, port=8888)
