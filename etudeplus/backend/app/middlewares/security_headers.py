"""
Security Headers Middleware
Adds comprehensive security headers to all responses.
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import os


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds security headers to all HTTP responses.
    Implements OWASP recommended security headers.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Get environment
        is_debug = os.getenv("DEBUG", "True").lower() == "true"
        
        # Content Security Policy
        # In production, this should be more restrictive
        if is_debug:
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: blob: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' ws: wss: http://localhost:*; "
                "frame-ancestors 'none';"
            )
        else:
            csp = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: blob: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' wss:; "
                "frame-ancestors 'none';"
            )
        
        response.headers["Content-Security-Policy"] = csp
        
        # HTTP Strict Transport Security (HSTS)
        # Only in production with HTTPS
        if not is_debug:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # X-Content-Type-Options: Prevents MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # X-Frame-Options: Prevents clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # X-XSS-Protection: Enables browser XSS filtering (legacy but still useful)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer-Policy: Controls how much referrer information is sent
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions-Policy (formerly Feature-Policy)
        # Restricts browser features
        permissions_policy = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=()"
        )
        response.headers["Permissions-Policy"] = permissions_policy
        
        # Cache-Control for API responses
        # Prevents caching of sensitive API data
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, proxy-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        
        # Remove server identification
        if "Server" in response.headers:
            del response.headers["Server"]
        
        # Add custom security header for API identification
        response.headers["X-Powered-By"] = "SchoolFlow Pro"
        
        return response


class CORSSecurityMiddleware(BaseHTTPMiddleware):
    """
    Enhanced CORS middleware with security-focused defaults.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Only add CORS headers for actual cross-origin requests
        origin = request.headers.get("Origin")
        if origin:
            # Validate origin against allowed list
            from app.core.config import settings
            
            allowed_origins = []
            if isinstance(settings.BACKEND_CORS_ORIGINS, str):
                allowed_origins = [o.strip() for o in settings.BACKEND_CORS_ORIGINS.split(",") if o.strip()]
            else:
                allowed_origins = list(settings.BACKEND_CORS_ORIGINS)
            
            # In debug mode, allow localhost origins
            is_debug = os.getenv("DEBUG", "True").lower() == "true"
            
            if origin in allowed_origins or (is_debug and "localhost" in origin):
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
                response.headers["Access-Control-Allow-Headers"] = (
                    "Authorization, Content-Type, X-Tenant-ID, X-Request-ID, "
                    "Accept, Origin, X-Requested-With"
                )
                response.headers["Access-Control-Max-Age"] = "86400"  # 24 hours
                response.headers["Access-Control-Expose-Headers"] = (
                    "X-Request-ID, X-RateLimit-Limit, X-RateLimit-Remaining, "
                    "X-RateLimit-Reset, X-Total-Count"
                )
        
        return response
