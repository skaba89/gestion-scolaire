"""
Middlewares package for SchoolFlow Pro.
"""
from app.middlewares.request_id import RequestIDMiddleware
from app.middlewares.tenant import TenantMiddleware
from app.middlewares.metrics import MetricsMiddleware
from app.middlewares.quota import QuotaMiddleware
from app.middlewares.security_headers import SecurityHeadersMiddleware, CORSSecurityMiddleware
from app.middlewares.rate_limit import RateLimitMiddleware, AdvancedRateLimiter

__all__ = [
    "RequestIDMiddleware",
    "TenantMiddleware",
    "MetricsMiddleware",
    "QuotaMiddleware",
    "SecurityHeadersMiddleware",
    "CORSSecurityMiddleware",
    "RateLimitMiddleware",
    "AdvancedRateLimiter",
]
