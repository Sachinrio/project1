import os
import json
import asyncio
import random
from datetime import datetime
from openai import AsyncOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Optional
from .browser_searcher import browser_searcher

# Define Pydantic models for Langchain parsing
class AgendaItem(BaseModel):
    time: str = Field(description="Time of the session (e.g., 10:00 AM)")
    title: str = Field(description="Title of the session")
    speaker: str = Field(description="Speaker name")

class EventContent(BaseModel):
    description: str = Field(description="Engaging event description")
    agenda: List[AgendaItem] = Field(description="List of agenda items")
    tags: List[str] = Field(description="List of relevant tags")
    image_prompt: str = Field(description="Detailed prompt for image generation")

class AIGeneratorService:
    def __init__(self):
        # 1. Initialize LLMs
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_model_name = os.getenv("GOOGLE_MODEL_NAME", "gemini-1.5-flash")
        
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_model_name = "llama-3.3-70b-versatile"

        self.llm_google = None
        self.llm_groq = None

        if self.google_api_key:
            print(f"Initializing Gemini (Text) with model: {self.google_model_name}")
            try:
                self.llm_google = ChatGoogleGenerativeAI(
                    temperature=0.7,
                    google_api_key=self.google_api_key,
                    model=self.google_model_name
                )
            except Exception as e:
                print(f"Failed to initialize Gemini: {e}")

        if self.groq_api_key:
            print(f"Initializing Groq (Text) with model: {self.groq_model_name}")
            try:
                from langchain_groq import ChatGroq
                self.llm_groq = ChatGroq(
                    temperature=0.7,
                    groq_api_key=self.groq_api_key,
                    model_name=self.groq_model_name
                )
            except Exception as e:
                 print(f"Failed to initialize Groq: {e}")

        if not self.llm_google and not self.llm_groq:
            print("WARNING: Neither GOOGLE_API_KEY nor GROQ_API_KEY working. AI features will be disabled.")
            
        # 2. Vision Filtering (Gemini-Based, No OCR required)
        self.ocr_enabled = False # Legacy flag for compatibility, if needed

        self.parser = JsonOutputParser(pydantic_object=EventContent)

    async def generate_event_content(self, title: str, category: str, start_time: str, end_time: str) -> dict:
        """
        Generates content using Google Gemini (Text) and DuckDuckGo (Image).
        Falls back to Groq or Manual defaults if Quota is exceeded.
        """
        # Prompt Construction
        prompt = f"""
        You are an expert event planner. Create detailed content for an event.
        
        Event Details:
        Title: {title}
        Category: {category}
        Time: {start_time} to {end_time}
        
        {self.parser.get_format_instructions()}
        
        Ensure description is 200-300 words, engaging, and uses plain text (no markdown headers).
        Ensure the image_prompt is highly detailed, cinematic, and photorealistic. It MUST explicitly visualize the core subject of the event title: "{title}".
        Example: If title is "AI Summit", prompt should include "futuristic robot, glowing neural networks". If "Yoga Class", then "peaceful park, people doing yoga".
        """

        result = {}
        success = False

        # 1. Try Google Gemini
        if self.llm_google:
            try:
                print(f"Generating Text with Gemini...")
                chain = self.llm_google | self.parser
                result = await chain.ainvoke(prompt)
                success = True
            except Exception as e:
                error_msg = str(e)
                print(f"Gemini Generation Failed: {error_msg}")
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    print("Gemini Quota Exceeded. Attempting fallback...")
                else:
                    print("Gemini error (non-quota). Attempting fallback...")

        # 2. Try Groq (Fallback)
        if not success and self.llm_groq:
            try:
                print(f"Generating Text with Groq (Fallback)...")
                chain = self.llm_groq | self.parser
                result = await chain.ainvoke(prompt)
                success = True
            except Exception as e:
                 print(f"Groq Generation Failed: {e}")

        # 3. Last Resort: Default Content
        if not success:
            print("All AI Generation failed or disabled. returning default content.")
            result = {
                "description": f"Join us for {title}! This event falls under the {category} category. (AI content generation unavailable, please edit description).",
                "agenda": [
                    {"time": start_time, "title": "Opening", "speaker": "Organizer"}
                ],
                "tags": ["Event", category],
                "image_prompt": title # Keep title as prompt for search
            }

        # Post-processing (Common)
        try:
            if "description" in result:
                result["description"] = self._clean_description(result["description"])

            # 4. Generate Image (DuckDuckGo Lite Proxy)
            from .image_scraper import image_scraper_service
            print(f"DEBUG: Starting Fast DDG Proxy Image Search for: {title}")
            try:
                # Use a fast 10-second timeout
                image_url = await asyncio.wait_for(image_scraper_service.get_image_url(title), timeout=10.0)
                if not image_url:
                    print("DEBUG: Proxy Image search returned nothing.")
                    result["imageUrl"] = ""
                else:
                    result["imageUrl"] = image_url
            except asyncio.TimeoutError:
                print("DEBUG: Image search hit global 10s limit.")
                result["imageUrl"] = ""
            except Exception as search_err:
                print(f"DEBUG: Image search crashed heavily: {search_err}.")
                result["imageUrl"] = ""

            return result

        except Exception as e:
            print(f"Error in post-processing/image search: {e}")
            # Even if image fails, return the text content we hopefully have
            return result

    async def _search_image(self, query: str) -> Optional[str]:
        """
        STRICT DuckDuckGo Search Strategy:
        1. Tries specific query: "{title} event image"
        2. Tries broader query: "{title}"
        3. Tries general query: "{category} event" (if available contextually)
        Returns ONLY images found on live DuckDuckGo results. No AI/curated fallbacks.
        """
        try:
            search_queries = [
                f"{query} image without text"
            ]

            # Stage 3 is removed to save time. 2 stages is enough for 20 seconds.
            for i, search_query in enumerate(search_queries):
                try:
                    print(f"DEBUG: DDG Search Stage {i+1} - Query: {search_query}")
                    results = await browser_searcher.search_images(search_query)
                    
                    if not results:
                        print(f"DEBUG: DDG Stage {i+1} returned NO results.")
                        continue

                    # Just return the very first image immediately
                    first_img = results[0]
                    print(f"DEBUG: SUCCESS - Grabbed first image directly: {first_img}")
                    return first_img
                            
                except Exception as stage_err:
                    print(f"DEBUG: DDG Search Stage {i+1} Error: {stage_err}")

            return ""
            
        except Exception as e:
            print(f"DEBUG: _search_image completely crashed ({e}). Returning None.")
            return None



    async def _is_image_clean(self, image_url: str) -> bool:
        """
        Uses Gemini Vision to detect if an image is suitable (no text/logos).
        Downloads image first to bypass 403 Forbidden blocks.
        Optimizes size to prevent 504 Deadline Exceeded errors.
        """
        if not self.llm_google:
            return True
        try:
            import requests
            import base64
            import io
            from PIL import Image
            from langchain_core.messages import HumanMessage
            
            # 1. Download image
            print(f"DEBUG: Vision - Downloading image: {image_url}")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            try:
                response = requests.get(image_url, headers=headers, timeout=12)
                if response.status_code != 200:
                    print(f"DEBUG: Vision Download Denied - Status {response.status_code} for {image_url}")
                    return False
            except Exception as download_err:
                print(f"DEBUG: Vision Download Failed - {download_err} for {image_url}")
                return False
                
            # 2. Optimize & Resize
            try:
                print(f"DEBUG: Vision - Resizing image ({len(response.content)} bytes)...")
                img = Image.open(io.BytesIO(response.content))
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                max_size = 800
                if img.width > max_size or img.height > max_size:
                    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                image_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
                print(f"DEBUG: Vision - Image compressed to {len(buffer.getvalue())} bytes.")
            except Exception as resize_err:
                print(f"DEBUG: Vision - Resizing failed, using raw: {resize_err}")
                image_data = base64.b64encode(response.content).decode("utf-8")
            
            # 3. Vision check
            message = HumanMessage(
                content=[
                    {"type": "text", "text": "Does this image contain any significant text, logos, or watermarks? Answer ONLY 'YES' or 'NO'."},
                    {
                        "type": "image_url", 
                        "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                    },
                ]
            )
            
            try:
                print("DEBUG: Vision - Invoking Gemini Vision model (8s timeout)...")
                # Tighten timeout for Render stability
                response = await asyncio.wait_for(self.llm_google.ainvoke([message]), timeout=8.0)
                decision = response.content.strip().upper()
                print(f"DEBUG: Vision - Gemini Decision: {decision}")
                return "NO" in decision
            except Exception as e:
                err_str = str(e).upper()
                if any(x in err_str for x in ["429", "504", "QUOTA", "DEADLINE", "TIMEOUT"]):
                    print(f"DEBUG: Vision - Quota/Timeout hit ({e}). BYPASSING check.")
                    return True 
                print(f"DEBUG: Vision - API Error: {e}")
                raise e
            
        except Exception as e:
            print(f"DEBUG: Vision check total failure: {e}")
            return True


    def _clean_description(self, text: str) -> str:
        """Removes markdown headers."""
        import re
        text = re.sub(r'^#+\s.*$', '', text, flags=re.MULTILINE)
        return text.strip()

# Initialize the service singleton
ai_service = AIGeneratorService()
