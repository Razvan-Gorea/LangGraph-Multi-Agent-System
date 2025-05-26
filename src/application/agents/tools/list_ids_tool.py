from langchain_core.tools import tool
from application.dbutils import DbUtils

def list_namespace_ids_tool(dbutils: DbUtils):

    @tool
    def list_ids(prefix: str, namespace: str):
        """
        This tool returns a list of all ids that are in use with the prefix. Returns a list of ids that are in use.
        The namespace is the name of the connector.
        """
        ids = dbutils.list_ids_in_namespace("quickstart", prefix, namespace)
        all_ids = []
        for each in ids:
            all_ids.extend(each)
        return all_ids

    return [list_ids]
