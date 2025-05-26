from fastapi import Depends, APIRouter, HTTPException
from typing import Annotated

from application.api.dependencies import get_sql_client, get_dbutils

from application.api.models.user import User
from application.api.models.permission import Permission
from application.api.models.user_with_permissions import UserWithPermissions
from application.api.sqlclient import SQLClient
from application.dbutils import DbUtils

userRouter = APIRouter()

SQLDep = Annotated[SQLClient, Depends(get_sql_client)]
DbUtilsDep = Annotated[DbUtils, Depends(get_dbutils)]

# user crud
@userRouter.get("/user/{user_id}")
def get_user_by_id(user_id: int, sqlclient: SQLDep) -> UserWithPermissions:
    user = sqlclient.get_by_id(User, user_id, eager_relationships=[User.permissions])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@userRouter.post("/user/login")
def login(login_attempt: User, sqlclient: SQLDep) -> User:
    user = sqlclient.get_by_email(User, login_attempt.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    else:
        if (sqlclient.compare_hash(login_attempt.password, user.password)): 
            return user
        else:
            raise HTTPException(status_code=404, detail="User not found")

@userRouter.post("/user/create")
def create_user(user: User, sqlclient: SQLDep) -> User:
    user = sqlclient.add_object(user)
    return user

@userRouter.put("/user/{user_id}")
def replace_user(user_id: int, user: User, sqlclient: SQLDep) -> User :
    user_replace = sqlclient.get_by_id(User, user_id)
    if not user_replace:
        raise HTTPException(status_code=404, detail="User not found")
    user = sqlclient.replace_object(user_replace, user)
    return user

@userRouter.delete("/user/{user_id}")
def delete_user(user_id: int, sqlclient: SQLDep):
    user = sqlclient.get_by_id(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    sqlclient.delete_object(user)
    return {"message": "User deleted"}

# permission crud
@userRouter.get("/permission/{permission_id}")
def get_permission(permission_id: int, sqlclient: SQLDep) -> Permission:
    permission = sqlclient.get_by_id(Permission, permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission

@userRouter.post("/permission/create")
def create_permission(permission: Permission, sqlclient: SQLDep) -> Permission:
    permission = sqlclient.add_object(permission)
    return permission

@userRouter.put("/permission/{permission_id}")
def update_permission(permission_id: int, permission: Permission, sqlclient: SQLDep) -> Permission:
    permission_replace = sqlclient.get_by_id(Permission, permission_id)
    if not permission_replace:
        raise HTTPException(status_code=404, detail="Permission not found")
    permission = sqlclient.replace_object(permission_replace, permission)
    return permission

@userRouter.delete("/permission/{permission_id}")
def delete_permission(permission_id: int, sqlclient: SQLDep):
    permission = sqlclient.get_by_id(Permission, permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    sqlclient.delete_object(permission)
    return {"message": "Permission deleted"}
