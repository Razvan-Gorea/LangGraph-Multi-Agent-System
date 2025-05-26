from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from application.api.models.user_permission import UserPermission
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    email: str = Field(index=True)
    password: str
    is_admin: Optional[bool] = Field(default=False)
    permissions: List["Permission"] = Relationship(back_populates="users", link_model=UserPermission)
