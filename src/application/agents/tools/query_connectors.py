from langchain_core.tools import tool

def create_connector_tool(connector_builder):
    
    @tool
    def query_rest_connector(connector_name: str, endpoint:str, params):
        """
        This tool takes an endpoint and parameters and hits that endpoint.
        It gives you back the response.
        """
        connector = connector_builder.get_connector(connector_name)
        res = connector.get(endpoint, params)
        return res

    @tool
    def query_postgres_connector(connector_name: str, query: str):
        """This tool takes your SQL query and executes it, returning the response.
           The connector_name parameter is just the name of the connector you want to connect to.
        """
        # get connector by name
        connector = connector_builder.get_connector(connector_name)
        res = connector.execute_sql_query(query)
        return res

    return [query_postgres_connector, query_rest_connector]
