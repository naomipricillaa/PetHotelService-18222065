# app/middleware/api_auth.py
from fastapi import Request, HTTPException
from fastapi.security import APIKeyHeader
from typing import List
import os
import secrets
import logging

logger = logging.getLogger(__name__)

# API Key header definition
API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

# Simpan API keys dalam dictionary atau database
# Untuk contoh ini menggunakan dictionary, tapi sebaiknya gunakan database untuk production
API_KEYS = {}

def generate_api_key(client_name: str) -> str:
    """Generate API key baru untuk client"""
    api_key = secrets.token_urlsafe(32)
    API_KEYS[api_key] = {
        "client_name": client_name,
        "is_active": True
    }
    return api_key

async def verify_api_key(request: Request):
    """Middleware untuk verifikasi API key"""
    try:
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            raise HTTPException(
                status_code=401,
                detail="API Key header is missing"
            )
        
        if api_key not in API_KEYS or not API_KEYS[api_key]["is_active"]:
            raise HTTPException(
                status_code=403,
                detail="Invalid or inactive API Key"
            )
        
        # Tambahkan client info ke request state
        request.state.client = API_KEYS[api_key]["client_name"]
        
    except Exception as e:
        logger.error(f"API authentication error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Authentication error occurred"
        )