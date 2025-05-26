from unittest.mock import MagicMock
from application.agents.tools.query_dbutils import create_pinecone_tool
from application.api.models.permission import Permission

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command
from langgraph.graph import END
from langchain_mistralai import ChatMistralAI

from application.agents.supervisor_agent.supervisor_agent import SupervisorAgent

def test_initialization(mock_env: MagicMock, mock_dbutils: MagicMock, mock_pinecone_tool: MagicMock):
    create_pinecone_tool.return_value = mock_pinecone_tool
    supervisor_agent = SupervisorAgent(mock_env, mock_dbutils)
    
    assert supervisor_agent.context_limit == 0
    assert supervisor_agent.gen_limit == 0
    assert supervisor_agent.members == ["gen", "context"]
    assert supervisor_agent.options == ["gen", "context", "FINISH"]
    assert isinstance(supervisor_agent.genclient, ChatMistralAI)
    assert "You are a supervisor" in supervisor_agent.system_prompt
    assert supervisor_agent.gen_agent is not None
    assert supervisor_agent.context_agent is not None
    assert supervisor_agent.graph is not None

def test_context_node(mock_chat_mistralai: MagicMock, supervisor_agent: SupervisorAgent, initial_state: dict):
    mock_output = {"role": "assistant", "content": "Context Facts", "name": "context_agent"}
    mock_chat_mistralai.return_value = mock_output
    result = supervisor_agent.context(initial_state)
    
    assert isinstance(result, Command)
    assert result.goto == "supervisor"
    assert len(result.update["messages"]) == 1
    assert result.update["messages"][0].content == "Context Facts"
    assert result.update["messages"][0].name == "context"

def test_context_node_empty_response(mock_chat_mistralai: MagicMock, supervisor_agent: SupervisorAgent, initial_state: dict):
    mock_output = {"role": "assistant", "content": ""}
    mock_chat_mistralai.return_value = mock_output
    result = supervisor_agent.context(initial_state)

    assert isinstance(result, Command)
    assert result.goto == "supervisor"
    assert len(result.update["messages"]) == 1
    assert result.update["messages"][0].content == "" # Empty content if no messages
    assert result.update["messages"][0].name == "context"

def test_gen_node(mock_chat_mistralai: MagicMock, supervisor_agent: SupervisorAgent, initial_state: dict):
    mock_output = {"role": "assistant", "content": "Gen Facts", "name": "gen_agent"}
    mock_chat_mistralai.return_value = mock_output
    result = supervisor_agent.gen(initial_state)

    assert isinstance(result, Command)
    assert result.goto == "supervisor"
    assert len(result.update["messages"]) == 1
    assert result.update["messages"][0].content == "Gen Facts"
    assert result.update["messages"][0].name == "gen"

def test_gen_node_empty_response(mock_chat_mistralai: MagicMock, supervisor_agent: SupervisorAgent, initial_state: dict):
    mock_output = {"role": "assistant", "content": ""}
    mock_chat_mistralai.return_value = mock_output
    result = supervisor_agent.gen(initial_state)

    assert isinstance(result, Command)
    assert result.goto == "supervisor"
    assert len(result.update["messages"]) == 1
    assert result.update["messages"][0].content == "" # Empty content if no messages
    assert result.update["messages"][0].name == "gen"

def test_supervisor_node_chooses_context(mock_chat_mistralai_structured: MagicMock, supervisor_agent: SupervisorAgent, initial_state: dict):
    mock_router = MagicMock()
    mock_router.invoke.return_value = {"next": "context"}
    mock_chat_mistralai_structured.return_value = mock_router
    result = supervisor_agent.supervisor(initial_state)

    assert isinstance(result, Command)
    assert result.goto == "context"
    assert result.update == {"next": "context"}
    assert supervisor_agent.context_limit == 1
    assert supervisor_agent.gen_limit == 0

def test_supervisor_node_chooses_gen(mock_chat_mistralai_structured: MagicMock, supervisor_agent: SupervisorAgent, initial_state: dict):
    mock_router = MagicMock()
    mock_router.invoke.return_value = {"next": "gen"}
    mock_chat_mistralai_structured.return_value = mock_router
    result = supervisor_agent.supervisor(initial_state)

    assert isinstance(result, Command)
    assert result.goto == "gen"
    assert result.update == {"next": "gen"}
    assert supervisor_agent.context_limit == 0
    assert supervisor_agent.gen_limit == 1

def test_supervisor_node_chooses_finish_and_gen_limit_reached(mock_chat_mistralai_structured: MagicMock, supervisor_agent: SupervisorAgent, initial_state: dict):
    supervisor_agent.gen_limit = 3
    mock_router = MagicMock()
    mock_router.invoke.return_value = {"next": "FINISH"}
    mock_chat_mistralai_structured.return_value = mock_router
    result = supervisor_agent.supervisor(initial_state)

    assert isinstance(result, Command)
    assert result.goto == "context" # Should go to context as gen limit reached
    assert result.update == {"next": "context"}
    assert supervisor_agent.context_limit == 1
    assert supervisor_agent.gen_limit == 3

def test_supervisor_node_chooses_finish_and_context_limit_reached(mock_chat_mistralai_structured: MagicMock, supervisor_agent: SupervisorAgent, initial_state: dict):
    supervisor_agent.context_limit = 3
    mock_router = MagicMock()
    mock_router.invoke.return_value = {"next": "FINISH"}
    mock_chat_mistralai_structured.return_value = mock_router
    result = supervisor_agent.supervisor(initial_state)

    assert isinstance(result, Command)
    assert result.goto == "gen" # Should go to gen as context limit reached
    assert result.update == {"next": "gen"}
    assert supervisor_agent.context_limit == 3
    assert supervisor_agent.gen_limit == 1

def test_supervisor_node_chooses_finish_and_both_limits_reached_and_both_called(mock_chat_mistralai_structured: MagicMock, supervisor_agent: SupervisorAgent, initial_state: dict):
    supervisor_agent.context_limit = 1
    supervisor_agent.gen_limit = 1
    mock_router = MagicMock()
    mock_router.invoke.return_value = {"next": "FINISH"}
    mock_chat_mistralai_structured.return_value = mock_router
    result = supervisor_agent.supervisor(initial_state)

    assert isinstance(result, Command)
    assert result.goto == END
    assert result.update == {"next": END}
    assert supervisor_agent.context_limit == 1
    assert supervisor_agent.gen_limit == 1

def test_supervisor_node_forces_gen_if_context_limit_reached_before_gen(mock_chat_mistralai_structured: MagicMock, supervisor_agent: SupervisorAgent, initial_state: dict):
    supervisor_agent.context_limit = 3
    mock_router = MagicMock()
    mock_router.invoke.return_value = {"next": "context"} # Even if it chooses context
    mock_chat_mistralai_structured.return_value = mock_router
    result = supervisor_agent.supervisor(initial_state)

    assert isinstance(result, Command)
    assert result.goto == "gen"
    assert result.update == {"next": "gen"}
    assert supervisor_agent.context_limit == 3
    assert supervisor_agent.gen_limit == 1

def test_supervisor_node_forces_context_if_gen_limit_reached_before_context(mock_chat_mistralai_structured: MagicMock, supervisor_agent: SupervisorAgent, initial_state: dict):
    supervisor_agent.gen_limit = 3
    
    mock_router = MagicMock()
    mock_router.invoke.return_value = {"next": "gen"} # even if it chooses gen
    mock_chat_mistralai_structured.return_value = mock_router

    result = supervisor_agent.supervisor(initial_state)

    assert isinstance(result, Command)
    assert result.goto == "context"
    assert result.update == {"next": "context"}
    assert supervisor_agent.context_limit == 1
    assert supervisor_agent.gen_limit == 3

def test_take_input_no_end_state(supervisor_agent: SupervisorAgent):
    mock_permission = MagicMock(spec=Permission)
    mock_permission.permission_name = "test_permission"
    mock_graph = MagicMock()
    supervisor_agent.graph = mock_graph
    mock_graph.stream.return_value = [
        ("start", {"messages": [HumanMessage(content="Test User Query"), HumanMessage(content="['test_permission']")]}),
        ("supervisor", {"next": "gen"}),
        ("gen", {"messages": [AIMessage(content="Final Answer", name="gen")]}),
        ("supervisor", {"next": "context"}), # No END state
    ]
    
    assert supervisor_agent.context_limit == 0
    assert supervisor_agent.gen_limit == 0

def test_take_input_empty_permissions(supervisor_agent: SupervisorAgent):
    mock_permission = MagicMock(spec=Permission)
    mock_permission.permission_name = "test_permission"
    mock_graph = MagicMock()
    supervisor_agent.graph = mock_graph

    mock_graph.stream.return_value = [
        ("start", {"messages": [HumanMessage(content="Test User Query"), HumanMessage(content="[]")]}),
        ("supervisor", {"next": "gen"}),
        ("gen", {"messages": [AIMessage(content="Final Answer", name="gen")]}),
        ("supervisor", {"next": END}),
        (END, {})
    ]

    result = supervisor_agent.take_input("Test User Query", [])
    assert result == None
    assert supervisor_agent.context_limit == 0
    assert supervisor_agent.gen_limit == 0

def test_take_input_supervisor_finishes_immediately(supervisor_agent: SupervisorAgent):
    mock_permission = MagicMock(spec=Permission)
    mock_permission.permission_name = "test_permission"
    mock_graph = MagicMock()
    supervisor_agent.graph = mock_graph
    mock_graph.stream.return_value = [
        ("start", {"messages": [HumanMessage(content="Test User Query"), HumanMessage(content="['test_permission']")]}),
        ("supervisor", {"next": "FINISH"}),
        ("FINISH", {})
    ]
    
    result = supervisor_agent.take_input("Test User Query", [mock_permission])

    assert result is None
    assert supervisor_agent.context_limit == 0
    assert supervisor_agent.gen_limit == 0
