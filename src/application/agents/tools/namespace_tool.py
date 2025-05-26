from langchain_core.tools import tool
from typing import List

def namespace_tool(dbutils):
    """Factory to allow access to the dbutils and not trip up the draconian pydantic."""
    @tool
    def namespace() -> List:
        """This tool returns a list, containing the names of all the namespaces on the pinecone index. Use this list to decide what namespace you should query."""
        query_namespaces = dbutils.get_namespaces("quickstart")
        return query_namespaces
    return namespace
