from fastapi import APIRouter, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import timedelta
from models.admin_schemas import LoginRequest, DashboardStats
from utils.admin_auth import authenticate_admin, create_access_token, get_current_admin
from utils.query_logger import query_logger
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])
admin_router = router  
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Display admin login page"""
    # Check if already logged in
    token = request.cookies.get("admin_session")
    if token:
        try:
            username = get_current_admin(request)
            if username:
                return RedirectResponse(url="/admin/dashboard", status_code=302)
        except:
            pass
    
    return templates.TemplateResponse("admin/login.html", {
        "request": request,
        "error": None
    })

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """Process admin login"""
    if not authenticate_admin(username, password):
        return templates.TemplateResponse("admin/login.html", {
            "request": request,
            "error": "Invalid username or password"
        }, status_code=401)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": username},
        expires_delta=timedelta(minutes=settings.SESSION_EXPIRE_MINUTES)
    )
    
    # Redirect to dashboard with cookie
    response = RedirectResponse(url="/admin/dashboard", status_code=302)
    response.set_cookie(
        key="admin_session",
        value=access_token,
        httponly=True,
        max_age=settings.SESSION_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    
    logger.info(f"Admin {username} logged in successfully")
    return response

@router.get("/logout")
async def logout():
    """Logout admin"""
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie("admin_session")
    return response

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Display admin dashboard"""
    try:
        # Check authentication
        username = get_current_admin(request)
        
        # Get statistics
        stats = query_logger.get_stats()
        recent_logs = query_logger.get_recent_logs(limit=20)
        
        return templates.TemplateResponse("admin/dashboard.html", {
            "request": request,
            "username": username,
            "stats": stats,
            "recent_logs": recent_logs
        })
    except HTTPException:
        return RedirectResponse(url="/admin/login", status_code=302)

@router.get("/logs", response_class=HTMLResponse)
async def logs_page(request: Request):
    """Display all logs"""
    try:
        username = get_current_admin(request)
        
        all_logs = query_logger.get_all_logs(limit=500)
        # Convert to list and reverse to show newest first
        logs_list = list(all_logs)
        logs_list.reverse()
        
        return templates.TemplateResponse("admin/logs.html", {
            "request": request,
            "username": username,
            "logs": logs_list
        })
    except HTTPException:
        return RedirectResponse(url="/admin/login", status_code=302)

@router.get("/stats", response_class=HTMLResponse)
async def stats_page(request: Request):
    """Display detailed statistics"""
    try:
        username = get_current_admin(request)
        
        stats = query_logger.get_stats()
        
        return templates.TemplateResponse("admin/stats.html", {
            "request": request,
            "username": username,
            "stats": stats
        })
    except HTTPException:
        return RedirectResponse(url="/admin/login", status_code=302)