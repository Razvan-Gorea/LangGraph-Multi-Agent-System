import pytest
from application.agents.integration_agent.pinecone_schema import PineconeSchemaHolder

ROWS = [{"id": "day-1", "text": "Today is Tuesday"}]

def test_parses_plain_json():
    assert PineconeSchemaHolder.from_llm_text('{"pinecone_items": [{"id": "day-1", "text": "Today is Tuesday"}]}').repr() == ROWS

def test_parses_fenced_json_in_content_blocks():
    blocks = [{"type": "text", "text": 'Here:\n```json\n{"pinecone_items": [{"id": "day-1", "text": "Today is Tuesday"}]}\n```'}]
    assert PineconeSchemaHolder.from_llm_text(blocks).repr() == ROWS

def test_rejects_non_json():
    with pytest.raises(ValueError):
        PineconeSchemaHolder.from_llm_text("no data")
