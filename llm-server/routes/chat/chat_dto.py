from pydantic import BaseModel, Field


class ChatInput(BaseModel):
    content: str = Field(..., alias="content", min_length=2)
    session_id: str = Field(..., alias="session_id")
    headers: dict = {}