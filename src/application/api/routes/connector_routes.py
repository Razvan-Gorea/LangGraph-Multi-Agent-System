from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

from application.api.dependencies import get_sql_client, get_environment, get_connector_manager
from application.api.sqlclient import SQLClient
from application.environment import Environment
from application.api.models.connector import Connector
from application.connectors.connector_builder import ConnectorBuilder

connectorRouter = APIRouter()

SQLDep = Annotated[SQLClient, Depends(get_sql_client)] 
EnvDep = Annotated[Environment, Depends(get_environment)]
ConnectorDep = Annotated[ConnectorBuilder, Depends(get_connector_manager)]

@connectorRouter.get("/connector/all")
def get_all_connectors(sqlclient: SQLDep) -> list[Connector]:
    return sqlclient.get_all_records(Connector)

@connectorRouter.get("/connector/{name}")
def get_connector(name: str, sqlclient: SQLDep) -> Connector:
    connector = sqlclient.get_by_column(Connector, "name", name)
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not Found")
    return connector

@connectorRouter.post("/connector/new")
def create_connector(connector: Connector, sqlclient: SQLDep, connector_manager: ConnectorDep) -> Connector:
    new_connector = sqlclient.add_object(connector)
    connector_manager.add_new_connector(new_connector)
    return new_connector

@connectorRouter.get("/connector/{name}/status")
def get_connector_status(name: str, connector_manager: ConnectorDep):
    connector = connector_manager.get_connector(name)

    if not connector:
        raise HTTPException(status_code=404, detail="Connector not Found")
    return connector.active
