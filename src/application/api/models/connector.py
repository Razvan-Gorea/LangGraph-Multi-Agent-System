from sqlmodel import SQLModel, Field, JSON, Column
from typing import Dict, Any, Optional

class Connector(SQLModel, table=True):
    id : Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    type_c: str
    c_params: Dict[str, Any] = Field(sa_column=Column(JSON))
    e_params: Dict[str, Any] = Field(sa_column=Column(JSON))
