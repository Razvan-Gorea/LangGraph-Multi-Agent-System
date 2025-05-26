from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional

from application.api.models.conversation import Conversation

class Chat(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    body: str = Field(index=True)
    last_modified_date: Optional[datetime] = Field(default_factory=datetime.utcnow)
    conversation_id: Optional[int] = Field(default=None, foreign_key="conversation.id")
    conversation: Optional["Conversation"] = Relationship(back_populates="chats")
