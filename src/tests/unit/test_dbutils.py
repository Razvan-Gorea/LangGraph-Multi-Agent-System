import pytest
from application.dbutils import DbUtils
from application.environment import Environment
from pinecone import QueryResponse, NotFoundException, ServerlessSpec

@pytest.fixture
def mock_env(mocker):
    '''A mock for environment'''
    env_mock = mocker.MagicMock(spec=Environment)
    env_mock.PINECONE_API_KEY = "fake-api-key"
    env_mock.DEBUG_MODE = True
    return env_mock

@pytest.fixture
def mock_pinecone_client(mock_env, mocker):
    '''A mock for pinecone'''
    mock_client = mocker.MagicMock()
    db_utils = DbUtils(
        env=mock_env,
        generator_batch_size=2,
        upsert_batch_size=2,
        embedding_model="fake-model"
    )
    db_utils.client = mock_client
    return db_utils, mock_client

def test_get_client(mock_env, mock_pinecone_client):
    '''A test for getting the client'''
    db_utils, _ = mock_pinecone_client

    client = db_utils.get_client(mock_env)
    assert client is not None


def test_create_index(mock_pinecone_client, mocker):
    '''A test for creating an index'''
    db_utils, mock_client = mock_pinecone_client
    
    db_utils.create_index("test-index", dimension=128)

    call_args = mock_client.create_index.call_args_list[0][1]

    assert call_args["name"] == "test-index"
    assert call_args["dimension"] == 128
    assert call_args["metric"] == "cosine"
    assert call_args["spec"].cloud == "aws"
    assert call_args["spec"].region == "us-east-1"


def test_create_embedding(mock_pinecone_client, mocker):
    '''A test for creating an embedding'''
    db_utils, mock_client = mock_pinecone_client
    
    mock_embedding_response = [{"values": [0.1, 0.2, 0.3]}, {"values": [0.4, 0.5, 0.6]}]
    mock_client.inference.embed.return_value = mock_embedding_response

    data = [{"text": "sample text 1"}, {"text": "sample text 2"}]

    embeddings = db_utils.create_embedding(data)

    mock_client.inference.embed.assert_called_with(
        model="fake-model",
        inputs=["sample text 1", "sample text 2"],
        parameters={"input_type": "passage", "truncate": "END"}
    )

    assert len(embeddings) == 2
    assert isinstance(embeddings, list)
    assert isinstance(embeddings[0], dict)

    # Check the contents of the embeddings
    assert "values" in embeddings[0]
    assert embeddings[0]["values"] == [0.1, 0.2, 0.3]
    assert embeddings[1]["values"] == [0.4, 0.5, 0.6]

def test_upsert_embeddings(mock_pinecone_client, mocker):
    db_utils, mock_client = mock_pinecone_client

    # Mock the response for upsert operation
    mock_response = {"upserted_count": 2}
    mock_client.Index.return_value.upsert.return_value = mock_response

    embeddings = [{"id": "1", "values": [0.1, 0.2, 0.3]}]
    upserted_count = db_utils.upsert_embeddings("test-index", "namespace", embeddings)

    # Verify the upsert method was called
    assert upserted_count == 2
    mock_client.Index.return_value.upsert.assert_called()


def test_search(mock_pinecone_client, mocker):
    '''A test to see if we can search for embeddings'''
    db_utils, mock_client = mock_pinecone_client

    mock_search_response = mocker.MagicMock(spec=QueryResponse)
    mock_search_response.matches = [{"id": "1", "score": 0.9}]
    mock_client.Index.return_value.query.return_value = mock_search_response

    embedding = [{"values": [0.1, 0.2, 0.3]}]
    result = db_utils.search("test-index", "namespace", embedding, result_amount=3)

    # Check that the search returned the expected result
    assert len(result) != 0

def test_index_exists(mock_pinecone_client, mocker):
    db_utils, mock_client = mock_pinecone_client

    # Simulate the case where the index exists (no exception)
    mock_client.describe_index.return_value = None
    exists = db_utils.index_exists("test-index")
    assert exists is True
    mock_client.describe_index.assert_called_with("test-index")

    # Simulate the case where the index does not exist (NotFoundException)
    mock_client.describe_index.side_effect = NotFoundException("Index not found")
    exists = db_utils.index_exists("test-index")
    assert exists is False


def test_describe_index(mock_pinecone_client, mocker):
    db_utils, mock_client = mock_pinecone_client

    # Simulate a successful describe index call
    mock_index_model = mocker.MagicMock()
    mock_client.describe_index.return_value = mock_index_model

    result = db_utils.describe_index("test-index")
    assert result == mock_index_model
    mock_client.describe_index.assert_called_with("test-index")

def test_get_namespaces(mock_pinecone_client, mocker):
    '''A test for getting namespaces from an index'''
    db_utils, mock_client = mock_pinecone_client

    # Mock the index object and its describe_index_stats method
    mock_index = mocker.MagicMock()
    mock_client.Index.return_value = mock_index

    # Scenario 1: Namespaces are present in the response
    mock_index.describe_index_stats.return_value = {
        'namespaces': {
            'ns1': {},
            'ns2': {}
        }
    }

    namespaces = db_utils.get_namespaces("test-index")

    assert namespaces == ['ns1', 'ns2']
    mock_client.Index.assert_called_with("test-index")

    mock_index.describe_index_stats.reset_mock()

    # Scenario 2: No namespaces are present in the response
    mock_index.describe_index_stats.return_value = {
        'namespaces': {}
    }

    namespaces = db_utils.get_namespaces("test-index")

    assert namespaces == []
    mock_client.Index.assert_called_with("test-index")

    # Scenario 3: The 'namespaces' key is not present in the response
    mock_index.describe_index_stats.return_value = {}

    namespaces = db_utils.get_namespaces("test-index")

    assert namespaces == []
    mock_client.Index.assert_called_with("test-index")