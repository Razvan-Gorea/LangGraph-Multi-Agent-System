from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional
from application.api.models.user_permission import UserPermission
class Permission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    permission_name: str = Field(index=True)
    users: List["User"] = Relationship(back_populates="permissions", link_model=UserPermission)
