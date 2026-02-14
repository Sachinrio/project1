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
        self.google_model_name = os.getenv("GOOGLE_MODEL_NAME", "gemini-2.5-flash")
        
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
            
        # 2. Initialize EasyOCR for text detection (CNN)
        print("Initializing EasyOCR (this may take a moment)...")
        try:
            # Skip EasyOCR on Render Free Tier to save memory (avoid OOM)
            if os.getenv("RENDER"):
                print("Running on Render: Disabling EasyOCR to save memory.")
                raise ImportError("Disabled on Render")

            import easyocr
            # 'en' for English. gpu=False to be safe on standard servers, true if CUDA avail.
            # Using CPU to avoid CUDA dependency hell for now unless user asked for GPU.
            self.reader = easyocr.Reader(['en'], gpu=False) 
            self.ocr_enabled = True
        except ImportError:
            print("EasyOCR not installed. Text filtering disabled.")
            self.ocr_enabled = False
        except Exception as e:
            print(f"EasyOCR Init Failed: {e}")
            self.ocr_enabled = False

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

            # Generate Image (DuckDuckGo Search)
            search_term = result.get("image_prompt", title)
            
            if search_term:
                print(f"Searching for image using: {search_term}")
                image_url = self._search_image(search_term)
                if image_url:
                    result["imageUrl"] = image_url
                    print(f"Image found: {result['imageUrl']}")
                else:
                    # Fallback to title if detailed prompt finds nothing
                    if search_term != title:
                        print(f"No image found for prompt, retrying with title: {title}")
                        image_url = self._search_image(title)
                        if image_url:
                            result["imageUrl"] = image_url
                        else:
                             result["imageUrl"] = ""
                    else:
                        result["imageUrl"] = ""
            else:
                result["imageUrl"] = ""

            return result

        except Exception as e:
            print(f"Error in post-processing/image search: {e}")
            # Even if image fails, return the text content we hopefully have
            return result

    def _search_image(self, query: str) -> Optional[str]:
        """
        Searches DuckDuckGo for images (Primary). 
        Falls back to curated Unsplash images if blocked/failed.
        """
        try:
            from duckduckgo_search import DDGS
            
            # Refine query for high-relevance professional event photos
            search_query = f"{query} professional event background"
            print(f"Attempting DDG Search for: {search_query}")
            
            with DDGS() as ddgs:
                results = list(ddgs.images(
                    keywords=search_query,
                    region="wt-wt",
                    safesearch="off",
                    max_results=5
                ))
                
                if results and len(results) > 0:
                     # Pick the first result for maximum relevance
                     image_url = results[0]['image']
                     print(f"DDG Success: {image_url}")
                     return image_url
                else:
                    # Retry with simpler query
                    print(f"DDG no results for '{search_query}', retrying simple title...")
                    with DDGS() as ddgs:
                        retry = list(ddgs.images(keywords=query, max_results=3))
                        if retry: 
                            print(f"DDG Retry Success: {retry[0]['image']}")
                            return retry[0]['image']
        except Exception as e:
            print(f"DDG Search Failed: {e}")

        # Curated fallbacks
        fallbacks = [
            "https://images.unsplash.com/photo-1540575861501-7ad05823c9f5?auto=format&fit=crop&w=1000&q=80",
            "https://images.unsplash.com/photo-1511578314322-379afb476865?auto=format&fit=crop&w=1000&q=80",
            "https://images.unsplash.com/photo-1505373630103-89d00c2a5851?auto=format&fit=crop&w=1000&q=80"
        ]
        return random.choice(fallbacks)



    def _has_text(self, image_url: str) -> bool:
        """
        Downloads image and checks for text using EasyOCR.
        Returns True if text is detected.
        """
        try:
            import requests
            
            # Download image with timeout
            response = requests.get(image_url, timeout=5)
            if response.status_code != 200:
                print(f"Failed to download image for OCR: {response.status_code}")
                return True # Treat as "bad" to skip it
            
            image_bytes = response.content
            
            # Run OCR
            # detail=0 returns just the text strings found
            result = self.reader.readtext(image_bytes, detail=0)
            
            # If result list is not empty, text was found
            if len(result) > 0:
                print(f"Text detected: {result}")
                return True
            
            return False

        except Exception as e:
            print(f"OCR check failed: {e}")
            return True # conservative: if lookup fails, assume bad to skip



    def _clean_description(self, text: str) -> str:
        """Removes markdown headers."""
        import re
        text = re.sub(r'^#+\s.*$', '', text, flags=re.MULTILINE)
        return text.strip()

# Initialize the service singleton
ai_service = AIGeneratorService()
