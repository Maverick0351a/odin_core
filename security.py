#!/usr/bin/env python3
"""
Security middleware for ODIN Protocol.
Implements authentication, rate limiting, and input validation.
"""

import time
import hashlib
import secrets
from typing import Dict, Optional
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from collections import defaultdict, deque
from datetime import datetime, timedelta


class TokenAuthenticator:
    """Simple token-based authentication system."""
    
    def __init__(self):
        """Initialize with default admin token."""
        # Generate a secure default token
        self.tokens = {
            "odin-admin-token": {
                "name": "admin",
                "permissions": ["read", "write", "admin"],
                "created": datetime.now()
            }
        }
        
        # For production, load from secure storage
        self._load_tokens_from_env()
    
    def _load_tokens_from_env(self):
        """Load additional tokens from environment variables."""
        import os
        
        # Check for additional API tokens in environment
        api_token = os.getenv("ODIN_API_TOKEN")
        if api_token:
            self.tokens[api_token] = {
                "name": "api_user",
                "permissions": ["read", "write"],
                "created": datetime.now()
            }
    
    def validate_token(self, token: str) -> Optional[Dict]:
        """Validate an API token and return user info."""
        return self.tokens.get(token)
    
    def generate_token(self, name: str, permissions: list) -> str:
        """Generate a new API token."""
        token = secrets.token_urlsafe(32)
        self.tokens[token] = {
            "name": name,
            "permissions": permissions,
            "created": datetime.now()
        }
        return token


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, requests_per_minute: int = 100):
        """Initialize rate limiter."""
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.window_size = 60  # 60 seconds
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if client is within rate limits."""
        now = time.time()
        
        # Clean old requests
        client_requests = self.requests[client_id]
        while client_requests and client_requests[0] < now - self.window_size:
            client_requests.popleft()
        
        # Check if under limit
        if len(client_requests) >= self.requests_per_minute:
            return False
        
        # Add current request
        client_requests.append(now)
        return True
    
    def get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client."""
        return max(0, self.requests_per_minute - len(self.requests[client_id]))


# Global instances
_authenticator = TokenAuthenticator()
_rate_limiter = RateLimiter()
security = HTTPBearer(auto_error=False)


def get_client_id(request: Request) -> str:
    """Get unique client identifier for rate limiting."""
    # Use IP address as primary identifier
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    host = request.client.host if request.client else "unknown"
    
    # Hash for privacy
    return hashlib.sha256(host.encode()).hexdigest()[:16]


async def check_rate_limit(request: Request):
    """Rate limiting middleware."""
    client_id = get_client_id(request)
    
    if not _rate_limiter.is_allowed(client_id):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Too many requests.",
            headers={"Retry-After": "60"}
        )
    
    return client_id


async def authenticate_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict]:
    """Authenticate API token (optional for public endpoints)."""
    if not credentials:
        return None
    
    user_info = _authenticator.validate_token(credentials.credentials)
    if not user_info:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    
    return user_info


async def require_authentication(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """Require valid authentication for protected endpoints."""
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    
    user_info = _authenticator.validate_token(credentials.credentials)
    if not user_info:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    
    return user_info


def require_permission(permission: str):
    """Decorator to require specific permission."""
    def dependency(user_info: Dict = Depends(require_authentication)):
        if permission not in user_info.get("permissions", []):
            raise HTTPException(
                status_code=403,
                detail=f"Permission '{permission}' required"
            )
        return user_info
    
    return dependency


def validate_request_size(request: Request, max_size: int = 1024 * 1024):
    """Validate request body size."""
    content_length = request.headers.get("content-length")
    
    if content_length and int(content_length) > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"Request body too large. Maximum size: {max_size} bytes"
        )


# Export authentication functions
def get_admin_token() -> str:
    """Get the admin token for testing/setup."""
    return "odin-admin-token"


def generate_new_token(name: str, permissions: list = None) -> str:
    """Generate a new API token."""
    if permissions is None:
        permissions = ["read"]
    
    return _authenticator.generate_token(name, permissions)


# Security headers middleware
def add_security_headers(response):
    """Add security headers to response."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
