from fastapi import APIRouter, HTTPException, Request
from app.config import supabase
import logging
from typing import Optional, List, Dict, Any

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/search-hotels")
async def search_hotels(data: dict) -> Dict[str, Any]:
    try:
        # Extract search parameters
        location = data.get("location", "").strip()
        min_price = data.get("minPrice")
        max_price = data.get("maxPrice")
        pet_category = data.get("petCategory", "").strip()
        pet_size = data.get("petSize", "").strip()

        logger.info(f"Searching hotels with params: {data}")

        # Start building the query
        query = supabase.table("hotels").select("*")

        # Apply filters
        if location:
            query = query.ilike("location", f"%{location}%")
        
        if min_price is not None and min_price != "":
            query = query.gte("price_per_night", float(min_price))
            
        if max_price is not None and max_price != "":
            query = query.lte("price_per_night", float(max_price))
            
        if pet_category:
            query = query.contains("pet_categories", [pet_category])
            
        if pet_size:
            query = query.contains("pet_sizes", [pet_size])

        # Execute query and order by rating
        response = query.order("rating", desc=True).execute()

        if not response.data:
            return {"hotels": [], "message": "No hotels found matching your criteria"}

        return {
            "hotels": response.data,
            "message": f"Found {len(response.data)} hotels matching your criteria"
        }

    except ValueError as e:
        logger.error(f"Value error in search: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid search parameters: {str(e)}")
    except Exception as e:
        logger.error(f"Error searching hotels: {str(e)}")
        raise HTTPException(status_code=500, detail="Error searching hotels")

@router.post("/save-search")
async def save_search(data: dict):
    try:
        # Save search history logic here (your existing code)
        user_id = data.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")

        response = supabase.table("search_history").insert({
            "user_id": user_id,
            "location": data.get("location"),
            "min_price": data.get("minPrice"),
            "max_price": data.get("maxPrice"),
            "pet_category": data.get("petCategory"),
            "pet_size": data.get("petSize")
        }).execute()

        return {"message": "Search data saved successfully"}
    except Exception as e:
        logger.error(f"Error saving search: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")