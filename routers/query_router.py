from fastapi import APIRouter, HTTPException, status, Request
from models.schemas import QueryRequest, QueryResponse, HealthResponse
from services.ai_service import ai_service
from services.search_service import search_service
from utils.helpers import detect_language, sanitize_query, is_government_related, humanize_response
from utils.query_logger import query_logger
import logging
import time
from slowapi import Limiter
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)

router = APIRouter()

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="GovAI Bangladesh API is running"
    )


@limiter.limit("10/minute")
@router.post("/query", response_model=QueryResponse)
async def process_query(request: Request, query_request: QueryRequest):
    """
    Process user query and return AI-generated response
    
    Args:
        request: FastAPI request object
        query_request: Query request containing user question
    
    Returns:
        AI-generated response with sources
    """
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        clean_query = sanitize_query(query_request.query)
        
        if not clean_query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="প্রশ্ন খালি রাখা যাবে না"
            )
        
        logger.info(f"Processing query from {client_ip}: {clean_query}")
        
        # Detect language for better search
        detected_lang = detect_language(clean_query)
        logger.info(f"Detected language: {detected_lang}")
        
        # Check if government-related
        is_gov, gov_message = is_government_related(clean_query)
        logger.info(f"Government-related check: {gov_message}")
        
        # Perform search
        search_results = await search_service.search(
            query=clean_query,
            language=detected_lang
        )
        
        # Format search context
        search_context = search_service.format_search_context(search_results)
        
        # Generate AI response
        ai_response = await ai_service.generate_response(
            query=clean_query,
            search_results=search_results,
            search_context=search_context
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Log the query
        query_logger.log_query(
            query=clean_query,
            language=detected_lang,
            processing_time=processing_time,
            ip_address=client_ip,
            status="success"
        )
        
        # Prepare response
        response = QueryResponse(
            query=clean_query,
            answer=humanize_response(ai_response),
            sources=search_results if query_request.include_sources else None,
            processing_time=round(processing_time, 2)
        )
        
        logger.info(f"Query processed successfully in {processing_time:.2f}s")
        
        return response
        
    except HTTPException as e:
        # Log failed query
        processing_time = time.time() - start_time
        query_logger.log_query(
            query=query_request.query,
            language="unknown",
            processing_time=processing_time,
            ip_address=client_ip,
            status="error"
        )
        raise
    except Exception as e:
        # Log failed query
        processing_time = time.time() - start_time
        query_logger.log_query(
            query=query_request.query,
            language="unknown",
            processing_time=processing_time,
            ip_address=client_ip,
            status="error"
        )
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"প্রশ্ন প্রক্রিয়াকরণে সমস্যা হয়েছে: {str(e)}"
        )