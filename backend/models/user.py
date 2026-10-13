from typing import List, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: 'user' or 'assistant' or 'system'")
    content: str = Field(..., description="Message text content")


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="Chat message history")
    language: Optional[str] = Field(default="English", description="Target language")


class ChatResponse(BaseModel):
    response: str = Field(..., description="AI Assistant response text")
    disclaimer: str = Field(..., description="Standard medical educational disclaimer")
