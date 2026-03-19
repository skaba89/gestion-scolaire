"""
Advanced Rate Limiting Middleware
Implements user-based rate limiting with Redis backend.
"""
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Optional
import time
import redis
import json
from datetime import datetime


class AdvancedRateLimiter:
    """
    Advanced rate limiter with user-based limits and sliding window.
    Uses Redis for distributed rate limiting across multiple instances.
    """
    
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        
        # Rate limit configurations by role and endpoint
        self.rate_limits = {
            # Default limits (requests per minute)
            "default": {"limit": 100, "window": 60},
            # Role-based limits
            "roles": {
                "SUPER_ADMIN": {"limit": 1000, "window": 60},
                "TENANT_ADMIN": {"limit": 500, "window": 60},
                "DIRECTOR": {"limit": 300, "window": 60},
                "TEACHER": {"limit": 200, "window": 60},
                "STUDENT": {"limit": 100, "window": 60},
                "PARENT": {"limit": 100, "window": 60},
                "ACCOUNTANT": {"limit": 200, "window": 60},
                "STAFF": {"limit": 150, "window": 60},
            },
            # Endpoint-specific limits (more restrictive for sensitive endpoints)
            "endpoints": {
                "/auth/login": {"limit": 10, "window": 60},  # 10 login attempts per minute
                "/auth/refresh": {"limit": 30, "window": 60},
                "/auth/password-reset": {"limit": 5, "window": 300},  # 5 per 5 minutes
                "/payments": {"limit": 20, "window": 60},
                "/grades": {"limit": 100, "window": 60},
                "/attendance": {"limit": 100, "window": 60},
                "/export": {"limit": 10, "window": 60},
                "/import": {"limit": 5, "window": 60},
                "/students/bulk": {"limit": 5, "window": 60},
            },
            # IP-based limits for unauthenticated requests
            "unauthenticated": {"limit": 50, "window": 60},
        }
    
    def _get_key(self, identifier: str, endpoint: str = "default") -> str:
        """Generate Redis key for rate limiting."""
        return f"ratelimit:{identifier}:{endpoint}"
    
    def _get_user_identifier(self, request: Request) -> str:
        """Extract user identifier from request."""
        # Try to get user ID from JWT
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                from jose import jwt
                token = auth_header.split(" ")[1]
                # Decode without verification just to get the subject
                claims = jwt.get_unverified_claims(token)
                user_id = claims.get("sub")
                if user_id:
                    return f"user:{user_id}"
            except Exception:
                pass
        
        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"
        return f"ip:{request.client.host if request.client else 'unknown'}"
    
    def _get_user_roles(self, request: Request) -> list:
        """Extract user roles from JWT."""
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                from jose import jwt
                token = auth_header.split(" ")[1]
                claims = jwt.get_unverified_claims(token)
                return claims.get("realm_access", {}).get("roles", [])
            except Exception:
                pass
        return []
    
    def _get_limit_for_request(self, request: Request, user_roles: list) -> dict:
        """Determine the appropriate rate limit for a request."""
        path = request.url.path
        
        # Remove API prefix for matching
        if path.startswith("/api/v1"):
            path = path[7:]
        
        # Check for endpoint-specific limits first
        for endpoint, limit_config in self.rate_limits["endpoints"].items():
            if path.startswith(endpoint):
                return limit_config
        
        # Check role-based limits
        for role in user_roles:
            if role in self.rate_limits["roles"]:
                return self.rate_limits["roles"][role]
        
        # Fall back to unauthenticated limit if no roles
        if not user_roles:
            return self.rate_limits["unauthenticated"]
        
        # Default limit
        return self.rate_limits["default"]
    
    def check_rate_limit(self, request: Request) -> tuple[bool, dict]:
        """
        Check if request is within rate limits.
        Returns (is_allowed, rate_limit_info).
        """
        identifier = self._get_user_identifier(request)
        user_roles = self._get_user_roles(request)
        limit_config = self._get_limit_for_request(request, user_roles)
        
        limit = limit_config["limit"]
        window = limit_config["window"]
        
        key = self._get_key(identifier, "global")
        
        try:
            # Use sliding window algorithm with Redis
            now = time.time()
            window_start = now - window
            
            # Remove old entries
            self.redis_client.zremrangebyscore(key, 0, window_start)
            
            # Count current requests in window
            current_count = self.redis_client.zcard(key)
            
            # Calculate remaining
            remaining = max(0, limit - current_count)
            
            # Calculate reset time
            oldest = self.redis_client.zrange(key, 0, 0, withscores=True)
            reset_time = int(oldest[0][1] + window) if oldest else int(now + window)
            
            if current_count >= limit:
                return False, {
                    "limit": limit,
                    "remaining": 0,
                    "reset": reset_time,
                    "retry_after": reset_time - int(now),
                }
            
            # Add current request
            self.redis_client.zadd(key, {str(now): now})
            self.redis_client.expire(key, window)
            
            return True, {
                "limit": limit,
                "remaining": remaining - 1,
                "reset": reset_time,
            }
        
        except redis.RedisError:
            # If Redis is unavailable, allow the request (fail open)
            return True, {
                "limit": limit,
                "remaining": limit,
                "reset": int(now + window),
                "error": "Rate limiting unavailable",
            }
    
    def get_rate_limit_headers(self, rate_info: dict) -> dict:
        """Generate rate limit headers for response."""
        headers = {
            "X-RateLimit-Limit": str(rate_info["limit"]),
            "X-RateLimit-Remaining": str(rate_info["remaining"]),
            "X-RateLimit-Reset": str(rate_info["reset"]),
        }
        if "retry_after" in rate_info:
            headers["Retry-After"] = str(rate_info["retry_after"])
        return headers


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware that enforces rate limiting on all requests.
    """
    
    def __init__(self, app, redis_url: str):
        super().__init__(app)
        self.limiter = AdvancedRateLimiter(redis_url)
        # Paths to skip rate limiting
        self.skip_paths = [
            "/health",
            "/health/",
            "/metrics",
            "/metrics/",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for certain paths
        path = request.url.path
        if any(path.startswith(skip) for skip in self.skip_paths):
            return await call_next(request)
        
        # Skip OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Check rate limit
        is_allowed, rate_info = self.limiter.check_rate_limit(request)
        
        if not is_allowed:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": rate_info.get("retry_after", 60),
                },
                headers=self.limiter.get_rate_limit_headers(rate_info),
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        for key, value in self.limiter.get_rate_limit_headers(rate_info).items():
            response.headers[key] = value
        
        return response
