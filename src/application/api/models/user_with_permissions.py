from typing import List
from sqlmodel import SQLModel

class PermissionRead(SQLModel):
    id: int
    permission_name: str

class UserWithPermissions(SQLModel):
    id: int
    username: str
    email: str
    is_admin: bool
    permissions: List[PermissionRead] = []