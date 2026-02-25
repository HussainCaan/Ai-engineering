from pydantic import BaseModel, Field
from typing import Annotated

########################### PYDANTIC MODEL #######################################
class Query(BaseModel):
    query: Annotated[str, Field(description="The query to be processed by the LLM")]