from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
from typing import Callable
from database.analytics_model import Analytics
import analytics.crud as analytics_db
import asyncio
from analytics.excluded_paths import EXCLUDE_PATHS

class AnalyticsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track API requests and bandwidth usage.
    Records request count, request/response sizes, and response times.
    """
    
    def __init__(self, app: ASGIApp, exclude_paths: list = None):
        super().__init__(app)
        # Paths to exclude from analytics (e.g., health checks, docs)
        self.exclude_paths = exclude_paths or EXCLUDE_PATHS
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip analytics for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Record start time
        start_time = time.time()
        
        # Get client IP
        client_ip = request.client.host if request.client else None
        # Check for forwarded IP (if behind proxy)
        if "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
        
        # Get user agent
        user_agent = request.headers.get("user-agent")
        
        # Calculate request size
        request_size = 0
        if "content-length" in request.headers:
            try:
                request_size = int(request.headers["content-length"])
            except ValueError:
                pass
        else:
            # If no content-length, read body to calculate size
            # Note: This will consume the body, so we need to store it
            body_bytes = await request.body()
            request_size = len(body_bytes)
            
            # Recreate request with body for downstream processing
            async def receive():
                return {"type": "http.request", "body": body_bytes}
            request._receive = receive
        
        # Process request
        response = await call_next(request)
        
        # Calculate response time
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Calculate response size
        response_size = 0
        if "content-length" in response.headers:
            try:
                response_size = int(response.headers["content-length"])
            except ValueError:
                pass
        
        # If no content-length header, we need to read the response body
        if response_size == 0:
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            response_size = len(response_body)
            
            # Recreate response with body so it can be returned
            from starlette.responses import Response as StarletteResponse
            response = StarletteResponse(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        
        # Calculate total bandwidth
        total_bandwidth = request_size + response_size
        
        # Create analytics record
        analytics_record = Analytics(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            request_size=request_size,
            response_size=response_size,
            total_bandwidth=total_bandwidth,
            client_ip=client_ip,
            user_agent=user_agent,
            response_time_ms=round(response_time, 2)
        )
        
        # Store analytics asynchronously (don't block response)
        # Use asyncio.create_task to run in background
        asyncio.create_task(analytics_db.create_analytics_record(analytics_record))
        
        return response

