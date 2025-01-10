from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.config import supabase
import logging
from typing import List, Dict
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from ..middleware.api_auth import verify_api_key, generate_api_key
from typing import Dict


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)

@router.get("/generate-api-key/{client_name}")
async def create_api_key(client_name: str):
    """Endpoint untuk generate API key baru"""
    api_key = generate_api_key(client_name)
    return {"client_name": client_name, "api_key": api_key}

@router.get("/recommendations", dependencies=[Depends(verify_api_key)])
async def get_recommendations(request: Request):
    """Protected recommendations endpoint"""
    client_name = request.state.client
    # Implementasi logic rekomendasi Anda di sini
    return {
        "client": client_name,
        "recommendations": [
            # data rekomendasi Anda
        ]
    }

def get_user_search_history(user_id: str) -> List[Dict]:
    try:
        # Get search history from last 30 days for more relevant recommendations
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        result = supabase.table("search_history")\
            .select("*")\
            .eq("user_id", user_id)\
            .gte("created_at", thirty_days_ago)\
            .execute()
        return result.data
    except Exception as e:
        logger.error(f"Error fetching search history: {str(e)}")
        return []

def get_all_hotels() -> List[Dict]:
    try:
        result = supabase.table("hotels")\
            .select("*")\
            .execute()
        return result.data
    except Exception as e:
        logger.error(f"Error fetching hotels: {str(e)}")
        return []

def normalize_score(score: float, min_score: float, max_score: float) -> float:
    if max_score == min_score:
        return 1.0
    return (score - min_score) / (max_score - min_score)

def calculate_hotel_scores(search_history: List[Dict], hotels: List[Dict]) -> List[Dict]:
    if not search_history or not hotels:
        return []

    hotel_scores = []
    
    # Calculate weights for different search history entries (more recent = higher weight)
    total_searches = len(search_history)
    weights = [(i + 1) / total_searches for i in range(total_searches)]
    
    for hotel in hotels:
        total_score = 0
        matches = 0
        
        for search, weight in zip(search_history, weights):
            score = 0
            
            # Location matching (exact match gets higher score)
            if search.get('location') and hotel.get('location'):
                if search['location'].lower() == hotel['location'].lower():
                    score += 3 * weight
                elif search['location'].lower() in hotel['location'].lower():
                    score += 1 * weight
            
            # Price range matching
            if hotel.get('price_per_night'):
                min_price = search.get('min_price', 0)
                max_price = search.get('max_price', float('inf'))
                if min_price <= hotel['price_per_night'] <= max_price:
                    score += 2 * weight
            
            # Pet category matching
            if search.get('pet_category') and hotel.get('pet_categories'):
                if search['pet_category'] in hotel['pet_categories']:
                    score += 2 * weight
            
            # Pet size matching
            if search.get('pet_size') and hotel.get('pet_sizes'):
                if search['pet_size'] in hotel['pet_sizes']:
                    score += 2 * weight
            
            if score > 0:
                matches += 1
                total_score += score
        
        # Adjust final score based on number of matches and hotel rating
        if matches > 0:
            avg_score = total_score / matches
            rating_bonus = hotel.get('rating', 0) * 0.2  # Add rating bonus
            final_score = avg_score + rating_bonus
            
            hotel_scores.append({
                **hotel,
                'recommendation_score': final_score
            })
    
    # Normalize scores between 0 and 1
    if hotel_scores:
        scores = [h['recommendation_score'] for h in hotel_scores]
        min_score, max_score = min(scores), max(scores)
        
        for hotel in hotel_scores:
            hotel['recommendation_score'] = normalize_score(
                hotel['recommendation_score'], 
                min_score, 
                max_score
            )
    
    return sorted(hotel_scores, key=lambda x: x['recommendation_score'], reverse=True)

@router.get("/api/recommendations/{user_id}")
async def get_recommendations(user_id: str):
    try:
        # Get user's search history
        search_history = get_user_search_history(user_id)
        
        if not search_history:
            return JSONResponse(
                status_code=200,
                content={
                    "recommendations": [],
                    "message": "No search history found. Try searching for hotels first!"
                }
            )
        
        # Get all hotels
        hotels = get_all_hotels()
        
        if not hotels:
            return JSONResponse(
                status_code=200,
                content={
                    "recommendations": [],
                    "message": "No hotels available in the system."
                }
            )
        
        # Calculate recommendations
        recommendations = calculate_hotel_scores(search_history, hotels)
        
        # Return top 10 recommendations
        return JSONResponse(
            status_code=200,
            content={
                "recommendations": recommendations[:10],
                "message": "Recommendations generated successfully"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Error generating recommendations"
        )
    
@router.get("/recommendations/{user_id}")
async def get_recommendations(user_id: str):
    try:
        # Get user's search history
        search_history = get_user_search_history(user_id)
        
        if not search_history:
            return JSONResponse(
                status_code=200,
                content={
                    "recommendations": [],
                    "message": "No search history found. Try searching for hotels first!"
                }
            )
        
        # Get all hotels
        hotels = get_all_hotels()
        
        if not hotels:
            return JSONResponse(
                status_code=200,
                content={
                    "recommendations": [],
                    "message": "No hotels available in the system."
                }
            )
        
        # Calculate recommendations
        all_recommendations = calculate_hotel_scores(search_history, hotels)
        
        # Filter recommendations with score > 0.5 (50%)
        filtered_recommendations = [
            hotel for hotel in all_recommendations 
            if hotel['recommendation_score'] > 0.5
        ]
        
        if not filtered_recommendations:
            return JSONResponse(
                status_code=200,
                content={
                    "recommendations": [],
                    "message": "No hotels match your preferences"
                }
            )
        
        # Return top 10 from filtered recommendations
        return JSONResponse(
            status_code=200,
            content={
                "recommendations": filtered_recommendations[:10],
                "message": f"Found {len(filtered_recommendations)} hotels matching your preferences"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Error generating recommendations"
        )
