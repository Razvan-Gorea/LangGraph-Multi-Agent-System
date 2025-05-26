import os
import subprocess
import uvicorn

from contextlib import asynccontextmanager
from colorama import just_fix_windows_console
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware 

from config import env, sqlclient, connector_manager, integration_agent
from application.api.models.integration_prompt import IntegrationPrompt

from application.api.routes.user_routes import userRouter
from application.api.routes.chat_routes import chatRouter
from application.api.routes.seed_routes import seedRouter
from application.api.routes.connector_routes import connectorRouter

# startup event
@asynccontextmanager
async def lifespan(app: FastAPI):
    connector_manager.set_integration_agent(integration_agent)
    connector_manager.startup_all_connectors()
    yield
    # shutdown events
    # shutdown all the connectors (if needed)
    connector_manager.shutdown_all_connectors()

app = FastAPI(lifespan=lifespan)

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
    integration_agent.graph.invoke({
        "messages": [
            {"role": "user", "content": prompt.to_string()},
        ],
        "data_store": connector_name
    })
    return {"message": "Webhook received"}

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
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

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    os.chdir("../../..")
    uvicorn.run(app, host=env.LOCAL_HOST_BACKEND_IP, port=8888)
