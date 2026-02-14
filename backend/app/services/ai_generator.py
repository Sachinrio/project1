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

            # Generate Image (DuckDuckGo Search using exact title)
            search_term = title
            
            if search_term:
                print(f"Searching for image using: {search_term}")
                image_url = await self._search_image(search_term)
                if image_url:
                    result["imageUrl"] = image_url
                    print(f"Image found: {result['imageUrl']}")
                else:
                    # Fallback to title if detailed prompt finds nothing
                    if search_term != title:
                        print(f"No image found for prompt, retrying with title: {title}")
                        image_url = await self._search_image(title)
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

    async def _search_image(self, query: str) -> Optional[str]:
        """
        1. Searches DuckDuckGo for candidate images.
        2. Uses Gemini Vision to filter out images with text/watermarks.
        3. Returns the first 'clean' image.
        """
        try:
            from duckduckgo_search import DDGS
            
            # Use title + 'event' for a clean, related search
            search_query = f"{query} event"
            print(f"Attempting DDG Search (Vision Filter) for: {search_query}")
            
            with DDGS() as ddgs:
                results = list(ddgs.images(
                    keywords=search_query,
                    region="wt-wt",
                    safesearch="off",
                    max_results=8 # Get extra to allow for filtering
                ))
                
                if results and len(results) > 0:
                     # Check top 5 for text
                     for res in results[:5]:
                         img_url = res['image']
                         print(f"Vision Checking candidate image: {img_url}")
                         if await self._is_image_clean(img_url):
                             print(f"DDG Success (Clean Image Found): {img_url}")
                             return img_url
                         else:
                             print(f"Skipping candidate image with text: {img_url}")
                     
                     # If none of top were clean, return first as final resort
                     print("No 100% clean images found in top results. Using first candidate.")
                     return results[0]['image']

        except Exception as e:
            print(f"DDG Image Search Failed: {e}")

        # Fallback to curated list
        fallbacks = [
            "https://images.unsplash.com/photo-1540575861501-7ad05823c9f5?auto=format&fit=crop&w=1000&q=80",
            "https://images.unsplash.com/photo-1511578314322-379afb476865?auto=format&fit=crop&w=1000&q=80",
            "https://images.unsplash.com/photo-1505373630103-89d00c2a5851?auto=format&fit=crop&w=1000&q=80"
        ]
        return random.choice(fallbacks)

    async def _is_image_clean(self, image_url: str) -> bool:
        """
        Uses Gemini Vision to detect if an image is suitable (no text/logos).
        Downloads the image bytes first to bypass 403 Forbidden headers.
        """
        if not self.llm_google:
            return True
        try:
            import requests
            import base64
            
            # 1. Download image bytes with custom User-Agent
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = requests.get(image_url, headers=headers, timeout=5)
            if response.status_code != 200:
                print(f"Failed to download image for Vision check ({response.status_code}): {image_url}")
                return False # Skip if we can't see it
                
            image_data = base64.b64encode(response.content).decode("utf-8")
            
            # 2. Vision prompt via base64 to bypass crawler blocks
            from langchain_core.messages import HumanMessage
            message = HumanMessage(
                content=[
                    {"type": "text", "text": "Does this image contain any significant text, logos, or watermarks? Answer ONLY 'YES' or 'NO'."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                    },
                ]
            )
            response = await self.llm_google.ainvoke([message])
            decision = response.content.strip().upper()
            return "NO" in decision
        except Exception as e:
            print(f"Gemini Vision check failed for {image_url}: {e}")
            return True # Conservative: use it if check fails


    def _clean_description(self, text: str) -> str:
        """Removes markdown headers."""
        import re
        text = re.sub(r'^#+\s.*$', '', text, flags=re.MULTILINE)
        return text.strip()

# Initialize the service singleton
ai_service = AIGeneratorService()
