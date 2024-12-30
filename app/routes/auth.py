from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from app.config import settings, supabase
import httpx
import logging
from typing import Optional
from postgrest.exceptions import APIError
from datetime import datetime

router = APIRouter()

# Setup logging
logging.basicConfig(level=logging.INFO)

# Google OAuth URLs
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

@router.get("/login")
def login_with_google():
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.CALLBACK_URL,
        "response_type": "code",
        "scope": "email profile",
        "access_type": "offline",
    }
    auth_url = f"{GOOGLE_AUTH_URL}?{'&'.join([f'{key}={value}' for key, value in params.items()])}"
    logging.info(f"Generated Google OAuth URL: {auth_url}")
    return RedirectResponse(auth_url)

async def get_or_create_user(email: str, name: str) -> Optional[dict]:
    try:
        # First, try to find the existing user
        result = supabase.table("users").select("*").eq("email", email).execute()
        if result.data and len(result.data) > 0:
            logging.info(f"Found existing user with email: {email}")
            return result.data[0]
        
        # If user doesn't exist, create new user
        logging.info(f"Creating new user with email: {email}")
        result = supabase.table("users").insert({
            "email": email,
            "name": name,
            # `created_at` is typically handled by the database as a default timestamp.
        }).execute()
        return result.data[0] if result.data else None
        
    except APIError as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database operation failed")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/callback")
async def callback(code: str):
    try:
        # Exchange code for token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": settings.CALLBACK_URL,
                    "grant_type": "authorization_code",
                    "code": code,
                },
            )
        token_response.raise_for_status()
        tokens = token_response.json()
        logging.info("Successfully received tokens from Google")

        # Get user information
        async with httpx.AsyncClient() as client:
            userinfo_response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {tokens['access_token']}"},
            )
        userinfo_response.raise_for_status()
        user_info = userinfo_response.json()
        logging.info(f"Successfully retrieved user info for email: {user_info.get('email')}")

        # Get or create user in database
        user = await get_or_create_user(
            email=user_info["email"],
            name=user_info.get("name", "")
        )
        
        if not user:
            raise HTTPException(status_code=500, detail="Failed to create or retrieve user")

        # Redirect to home page with user ID
        return RedirectResponse(url=f"/home?user_id={user['id']}")

    except httpx.HTTPError as e:
        logging.error(f"HTTP error during OAuth flow: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to complete OAuth flow")
    except KeyError as e:
        logging.error(f"Missing required field in response: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid response from Google")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
