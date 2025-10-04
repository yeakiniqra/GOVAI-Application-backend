from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class LoginRequest(BaseModel):
    """Admin login request"""
    username: str
    password: str

class LoginResponse(BaseModel):
    """Admin login response"""
    message: str
    username: str

class QueryLog(BaseModel):
    """Query log entry"""
    id: int
    timestamp: datetime
    query: str
    language: str
    processing_time: float
    ip_address: Optional[str]
    status: str

class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_queries: int
    queries_today: int
    avg_processing_time: float
    success_rate: float
    top_queries: List[dict]
    queries_by_hour: List[dict]
    queries_by_language: dict
    recent_queries: List[QueryLog]