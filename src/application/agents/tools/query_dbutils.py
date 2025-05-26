from langchain_core.tools import tool
from typing import Dict, List, Any

def create_pinecone_tool(dbutils):
    """
    Factory to allow access to the dbutils and not trip up the draconian pydantic.
    """
    @tool
    def query_dbutils(user_query: str, namespace: str) -> Dict[str, Any]:
        """
        Queries the vector database with semantic search.
        """
        
        query_embedding = dbutils.create_query_embedding(user_query)
        # the agent knows what to do with the tool through the tool decorator and the multi-string.
        results = dbutils.search(
            index_name="quickstart",
            namespace=namespace,
            embedding=query_embedding,
            result_amount=5
        )
        return(results)
    return query_dbutils
