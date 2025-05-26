from typing import Literal, Any, Dict
from typing_extensions import TypedDict
from langgraph.graph import MessagesState
from langchain_core.callbacks import BaseCallbackHandler
from colorama import Fore, Style

class GraphCallback(BaseCallbackHandler):
    def on_tool_end(self, output, run_id, parent_run_id, **kwargs) -> None:
        if output is not None:
            print(output.pretty_print())

    def on_tool_error(self, error, run_id, parent_run_id, **kwargs) -> None:
        print(error)

class State(MessagesState):
    next: str

class Router(TypedDict):
    # THIS SHOULD BE DYNAMIC
    next: Literal["context", "gen", "FINISH"]

# State of the integration agent
# When we re-format everything, maybe we move all this.
class IntegrationState(MessagesState):
    datastore: str
