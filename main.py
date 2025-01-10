from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, search, recommendations
import logging

# Initialize FastAPI app
app = FastAPI()

# Allowed origins (Menambahkan URL dengan URL yang diizinkan untuk mengakses API)
allowed_origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://pet-hotel-service-18222065.vercel.app",
    "https://pethotelservice.up.railway.app" ,
    "https://finalyze.up.railway.app/"
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(search.router, tags=["search"])
app.include_router(recommendations.router, prefix="/api", tags=["recommendations"])  # Tambahkan prefix

# Initialize templates
templates = Jinja2Templates(directory="app/templates")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/home", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})

@app.get("/recommendations", response_class=HTMLResponse)
async def recommendations_page(request: Request):
    return templates.TemplateResponse("recommendations.html", {"request": request})