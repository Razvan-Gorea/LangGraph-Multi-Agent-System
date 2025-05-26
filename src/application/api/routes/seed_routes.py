import json
from fastapi import Depends, APIRouter
from typing import Annotated

from application.api.dependencies import get_sql_client

from application.api.models.user import User
from application.api.models.permission import Permission
from application.api.models.conversation import Conversation
from application.api.models.user_permission import UserPermission
from application.api.models.connector import Connector

from application.api.sqlclient import SQLClient

seedRouter = APIRouter()

SQLDep = Annotated[SQLClient, Depends(get_sql_client)]

@seedRouter.get("/seed/user")
def seed_users_db(sqlclient: SQLDep) -> str:
    with open('application/seeds/database/user.json', 'r') as file:
        users_data = json.load(file)
        for user_data in users_data:
            permission_names = user_data.pop("permissions", [])
            user = User(**user_data)
            user = sqlclient.add_object(user)

            user_permissions_to_add = []

            for permission_name in permission_names:
                permissions = sqlclient.get_by_column(Permission, "permission_name", permission_name)
                if permissions:
                    permission = permissions[0]
                    user_permissions_to_add.append(UserPermission(user_id=user.id, permission_id=permission.id))
            
            if user_permissions_to_add:
                sqlclient.bulk_add_object(user_permissions_to_add)

    return "ok"

@seedRouter.get("/seed/permission")
def seed_permission_db(sqlclient: SQLDep) -> str:
    with open('application/seeds/database/permission.json', 'r') as file:
        permissions_data = json.load(file)
        permissions = [Permission(**permission) for permission in permissions_data]
        sqlclient.bulk_add_object(permissions)
    return "ok"

@seedRouter.get("/seed/conversation")
def seed_conversations_db(sqlclient: SQLDep) -> str:
    with open('application/seeds/database/conversation.json', 'r') as file:
        conversations_data = json.load(file)
        conversations = [Conversation(**conversation) for conversation in conversations_data]
        sqlclient.bulk_add_object(conversations)
    return "ok"

@seedRouter.get("/seed/connector")
def seed_connector_db(sqlclient: SQLDep) -> str:
    with open('application/seeds/connectors/connector_details.json', 'r') as file:
        connector_data = json.load(file)
        connectors = [Connector(**connector) for connector in connector_data]
        sqlclient.bulk_add_object(connectors)
    return "ok"

@seedRouter.get("/seed/all")
def seed_all_db(sqlclient: SQLDep) -> str:
   seed_connector_db(sqlclient)
   seed_permission_db(sqlclient)
   seed_users_db(sqlclient)
   seed_conversations_db(sqlclient)
   return "ok"
