from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.services.ai_generator import ai_service

router = APIRouter()

class GenerateEventRequest(BaseModel):
    title: str
    category: str = "Business"
    start_time: str = "10:00"
    end_time: str = "12:00"

@router.post("/generate-event")
async def generate_event(request: GenerateEventRequest):
    """
    Generates event details (description, agenda, tags, image) using AI.
    """
    try:
        # 1. Generate Content
        # 1. Generate Content
        content = await ai_service.generate_event_content(request.title, request.category, request.start_time, request.end_time)
        
        return content

    except Exception as e:
        print(f"AI Generation Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
