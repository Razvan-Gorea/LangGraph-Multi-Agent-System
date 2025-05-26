from sqlmodel import Session

def get_session():
    from config import sqlclient
    with Session(sqlclient.engine) as session:
        yield session

def get_sql_client():
    from config import sqlclient
    yield sqlclient

def get_dbutils():
    from config import dbutils
    yield dbutils

def get_environment():
    from config import env
    yield env

def get_supervisor_agent():
    from config import supervisor_agent
    yield supervisor_agent

def get_connector_manager():
    from config import connector_manager
    yield connector_manager
