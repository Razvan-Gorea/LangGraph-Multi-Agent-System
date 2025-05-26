from sqlmodel import Field, SQLModel
from typing import Optional

class UserPermission(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    permission_id: Optional[int] = Field(default=None, foreign_key="permission.id", primary_key=True)
