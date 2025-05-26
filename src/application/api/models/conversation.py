from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime

from typing import Optional

class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    last_modified_date: Optional[datetime] = Field(default_factory=datetime.utcnow)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    chats: list["Chat"] = Relationship(back_populates="conversation", cascade_delete=True)
