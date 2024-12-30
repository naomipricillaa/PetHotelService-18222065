from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.routes import auth
from app.config import supabase
from fastapi.staticfiles import StaticFiles
import logging
from typing import Optional

# Initialize FastAPI app
app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(auth.router, prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/home", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})

@app.post("/save-search")
async def save_search(request: Request):
    try:
        # Get JSON data from request body
        data = await request.json()
        
        # Log received data
        logger.info(f"Received search data: {data}")
        
        # Validate required fields
        user_id = data.get("user_id")
        if not user_id:
            logger.error("Missing user_id in request")
            return JSONResponse(
                status_code=400,
                content={"detail": "User ID is required"}
            )

        # Prepare data for Supabase
        search_data = {
            "user_id": user_id,
            "location": data.get("location"),
            "min_price": float(data.get("minPrice")) if data.get("minPrice") else None,
            "max_price": float(data.get("maxPrice")) if data.get("maxPrice") else None,
            "pet_category": data.get("petCategory"),
            "pet_size": data.get("petSize")
        }

        # Insert data into Supabase
        logger.info(f"Attempting to save search data: {search_data}")
        response = supabase.table("search_history").insert(search_data).execute()
        
        # Log response for debugging
        logger.info(f"Supabase response: {response}")

        return JSONResponse(
            status_code=200,
            content={"message": "Search data saved successfully"}
        )

    except ValueError as e:
        logger.error(f"Value error processing data: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"detail": f"Invalid data format: {str(e)}"}
        )
    except Exception as e:
        logger.error(f"Error saving search: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )