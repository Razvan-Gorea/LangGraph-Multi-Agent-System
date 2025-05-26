from application.environment import Environment
from application.dbutils import DbUtils
from application.api.sqlclient import SQLClient
from application.connectors.connector_builder import ConnectorBuilder
from application.agents.supervisor_agent.supervisor_agent import SupervisorAgent
from application.agents.integration_agent.integration_agent import IntegrationAgent

env = Environment()
env.load_environment()

dbutils = DbUtils(env, 96, 200, "multilingual-e5-large")


connect_args = {"check_same_thread": False}
sqlclient = SQLClient(env, connect_args)
sqlclient.create_db_and_tables()

connector_manager = ConnectorBuilder(sqlclient, "application/seeds/connectors/pinecone_schema.json")

supervisor_agent = SupervisorAgent(env, dbutils)
integration_agent = IntegrationAgent(env, dbutils, connector_manager)
