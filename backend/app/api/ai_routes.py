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
        import traceback
        error_msg = str(e)
        print(f"AI Generation CRITICAL FAILURE: {error_msg}")
        traceback.print_exc()
        # Ensure we return JSON, not text
        return {
            "error": "AI_GENERATION_FAILED",
            "detail": error_msg,
            "description": f"Join us for {request.title}! (AI content generation failed, please edit manually).",
            "agenda": [{"time": request.start_time, "title": "Opening", "speaker": "Organizer"}],
            "tags": ["Event", request.category],
            "imageUrl": "https://images.unsplash.com/photo-1540575861501-7cf05a4b125a?auto=format&fit=crop&w=1000&q=80"
        }
