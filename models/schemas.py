from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class QueryRequest(BaseModel):
    """Request model for user queries"""
    query: str = Field(..., description="User query in English, Bangla, or Banglish")
    user_id: Optional[str] = Field(None, description="Optional user identifier for tracking")
    include_sources: bool = Field(True, description="Whether to include source URLs in response")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "How do I apply for a passport?",
                "user_id": "user123",
                "include_sources": True
            }
        }


class SearchResult(BaseModel):
    """Model for individual search results"""
    title: str
    url: str
    snippet: Optional[str] = None
    score: Optional[float] = None


class QueryResponse(BaseModel):
    """Response model for AI-generated answers"""
    query: str
    answer: str = Field(..., description="AI-generated answer in Bangla")
    sources: Optional[List[SearchResult]] = Field(None, description="Source references used")
    timestamp: datetime = Field(default_factory=datetime.now)
    processing_time: Optional[float] = Field(None, description="Time taken to process in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "How do I apply for a passport?",
                "answer": "পাসপোর্টের জন্য আবেদন করতে আপনাকে অনলাইনে www.passport.gov.bd এ যেতে হবে...",
                "sources": [
                    {
                        "title": "Bangladesh Passport Application",
                        "url": "https://www.passport.gov.bd",
                        "snippet": "Official passport application portal"
                    }
                ],
                "timestamp": "2025-10-02T10:30:00",
                "processing_time": 2.5
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)