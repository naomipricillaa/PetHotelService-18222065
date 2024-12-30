from fastapi import APIRouter, HTTPException, Request
from app.config import supabase
import logging

router = APIRouter()
logging.basicConfig(level=logging.INFO)

@router.post("/save-search")
async def save_search(data: dict, request: Request):
    try:
        # Simpan data ke Supabase
        user_id = data.get("user_id")  # Pastikan user_id dikirimkan dari frontend
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
        
        if response.status_code != 201:
            raise HTTPException(status_code=500, detail="Failed to save search")

        return {"message": "Search data saved successfully"}
    except Exception as e:
        logging.error(f"Error saving search: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
