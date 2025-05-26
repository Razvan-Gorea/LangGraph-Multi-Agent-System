from fastapi import Depends, APIRouter
from typing import Annotated
from fastapi import HTTPException
from datetime import datetime
from typing import Any

from application.api.dependencies import get_sql_client, get_dbutils, get_environment, get_supervisor_agent
from application.api.models.conversation import Conversation
from application.api.models.chat import Chat
from application.api.models.user import User
from application.api.sqlclient import SQLClient
from application.agents.supervisor_agent.supervisor_agent import SupervisorAgent
from application.dbutils import DbUtils
from application.environment import Environment

chatRouter = APIRouter()

SQLDep = Annotated[SQLClient, Depends(get_sql_client)]
DbUtilsDep = Annotated[DbUtils, Depends(get_dbutils)]
EnvDep = Annotated[Environment, Depends(get_environment)]
SupervisorAgentDep = Annotated[SupervisorAgent, Depends(get_supervisor_agent)]

@chatRouter.post("/conversation/latest")
def get_last_conversation(user_id: int, sqlclient: SQLDep) -> Any:
    # we only want the last used conversation here
    conversation = sqlclient.get_latest_conversation(user_id)     
    return conversation

# conversation crud
@chatRouter.post("/conversation/all")
def get_all_conversations(user_id: int, sqlclient: SQLDep) -> list[Conversation]:
    conversations = sqlclient.get_by_column(Conversation, "user_id", user_id)
    return conversations    

@chatRouter.get("/conversation/{convo_id}")
def get_conversation(convo_id: int, sqlclient: SQLDep) -> Conversation:
    conversation = sqlclient.get_by_id(Conversation, convo_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@chatRouter.post("/conversation/create")
def create_conversation(conversation: Conversation, sqlclient: SQLDep) -> Conversation:
    conversation.last_modified_date = datetime.utcnow()
    conversation = sqlclient.add_object(conversation)
    return conversation

@chatRouter.put("/conversation/{convo_id}")
def update_conversation(convo_id: int, conversation: Conversation, sqlclient: SQLDep) -> Conversation:
    conversation.last_modified_date = datetime.utcnow()
    convo_replace = sqlclient.get_by_id(Conversation, convo_id)
    if not convo_replace:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conversation = sqlclient.replace_object(convo_replace, conversation)
    return conversation

@chatRouter.delete("/conversation/{convo_id}")
def delete_conversation(convo_id: int, sqlclient: SQLDep):
    conversation = sqlclient.get_by_id(Conversation, convo_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    sqlclient.delete_object(conversation)
    return {"message": "Conversation deleted"}


# chat crud
@chatRouter.get("/conversation/{convo_id}/chat/all")
def get_all_chats_in_conversation(convo_id: int, sqlclient: SQLDep) -> list[Chat]:
    chats = sqlclient.get_by_column(Chat, "conversation_id", convo_id)
    # give them back ordered by datemodified
    # TODO have a different way of chaining them to an order?
    return chats

@chatRouter.get("/conversation/{convo_id}/chat/{chat_id}")
def get_chat(chat_id: int, sqlclient: SQLDep) -> Chat:
    chat = sqlclient.get_by_id(Chat, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@chatRouter.post("/conversation/{convo_id}/chat/create")
def create_chat(convo_id: int, chat: Chat, sqlclient: SQLDep) -> Chat:
    
    chat.last_modified_date = datetime.utcnow()
    chat = sqlclient.add_object(chat)
    
    # we update the conversation to bump it to the top of the recent lists
    conversation = sqlclient.get_by_id(Conversation, convo_id)
    conversation.last_modified_date = datetime.utcnow()
    
    sqlclient.add_object(conversation)
    
    return chat

@chatRouter.post("/conversation/{convo_id}/chat/response")
def create_response(convo_id: int, chat: Chat, sqlclient: SQLDep, supervisor_agent: SupervisorAgentDep) -> Chat:
    conversation = sqlclient.get_by_id(Conversation, convo_id)
    conversation.last_modified_date = datetime.utcnow()
    
    user = sqlclient.get_by_id(User, conversation.user_id, eager_relationships=[User.permissions])
    
    answer = supervisor_agent.take_input(chat.body, user.permissions)
    final_result = "Response:" + str(answer)

    response = Chat(body=final_result, conversation_id=convo_id)
    
    sqlclient.add_object(response)
    
    return response

@chatRouter.delete("/conversation/{convo_id}/chat/{chat_id}")
def delete_chat(chat_id: int, sqlclient: SQLDep):
    chat = sqlclient.get_by_id(Chat, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    sqlclient.delete_object(chat)
    return {"message": "Chat deleted"}

@chatRouter.put("/conversation/{convo_id}/chat/{chat_id}")
def update_chat(chat_id: int, chat: Chat, sqlclient: SQLDep) -> Chat:
    chat.last_modified_date = datetime.utcnow()
    chat_replace = sqlclient.get_by_id(Chat, chat_id)
    if not chat_replace:
        raise HTTPException(status_code=404, detail="Chat not found")
    chat = sqlclient.replace_object(chat_replace, chat)
    return chat
