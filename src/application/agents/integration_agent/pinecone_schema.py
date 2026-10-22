from pydantic import BaseModel, Field
from typing import List

class PineconeSchema(BaseModel):
    """A single row in the pinecone."""
    id: str = Field(description="An id. Make sure it is not already in use.")
    text: str = Field(description="This should contain all of the data you collected.")
    
    def repr(self) -> dict:
        return {"id": self.id, "text": self.text}


class PineconeSchemaHolder(BaseModel):
    """Holder for each row in the pinecone."""
    pinecone_items: List[PineconeSchema] = Field(description="A list of pinecone rows.")

    def repr(self) -> List[dict]:
        return [item.repr() for item in self.pinecone_items]

    @classmethod
    def from_llm_text(cls, content) -> "PineconeSchemaHolder":
        """Parses the model's JSON reply. Models that reject forced tool_choice cant use response_format."""
        if isinstance(content, list):  # anthropic content blocks
            content = "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in content)
        # skip any prose or code fences around the object
        return cls.model_validate_json(content[content.index("{"): content.rindex("}") + 1])
