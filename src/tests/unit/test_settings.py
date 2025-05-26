from application.environment import Environment

def test_settings_loading():
    env = Environment()
    env.load_environment()

    assert env.PINECONE_API_KEY is not None
    assert env.DEBUG_MODE is not None
    assert env.SQL_LITE_DB_STRING is not None
    assert env.DEEPSEEK_API_KEY is not None
    assert env.LOCAL_HOST_BACKEND_IP is not None
    assert env.LOCAL_HOST_FRONTEND_IP is not None
