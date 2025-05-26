from application.environment import Environment
from application.api.sqlclient import SQLClient
from application.dbutils import DbUtils
from application.agents.supervisor_agent.supervisor_agent import SupervisorAgent
from application.api.models.user import User
from application.api.models.permission import Permission
from application.api.models.user_permission import UserPermission

def test_supervisor_agent_permissions(environment: Environment, sqlclient: SQLClient, dbutils: DbUtils):
    supervisor_agent = SupervisorAgent(environment, dbutils)

    # set up sql data
    test_user = User(
        id=1,
        username="test",
        email="test",
        password="test",
    )
    test_permission = Permission(
        id=1,
        permission_name="laptop_prices",
        user_id=1
    )
    test_user_permission = UserPermission(
        permission_id = 1,
        user_id = 1
    )

    sqlclient.add_object(test_user)
    sqlclient.add_object(test_permission)
    sqlclient.add_object(test_user_permission)

    user = sqlclient.get_by_id(User, test_user.id, eager_relationships=[User.permissions])

    result = supervisor_agent.take_input("Tell me about the macbook 1 in laptop_prices.", user.permissions)

    assert "laptop_prices" in result

def test_supervisor_agent_no_permissions(environment: Environment, dbutils: DbUtils, sqlclient: SQLClient):
    supervisor_agent = SupervisorAgent(environment, dbutils)

    test_user = User(
        id=1,
        username="hello",
        email="hello",
        password="hello"
    )

    sqlclient.add_object(test_user)

    user = sqlclient.get_by_id(User, 1, [User.permissions])
    result = supervisor_agent.take_input("Tell me about the macbook 1 in laptop_prices.", user.permissions)

