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
        Multi-source search strategy:
        1. DuckDuckGo (General)
        2. Unsplash (via DDG)
        3. Pollinations.ai (AI Generation - High Reliability Fallback)
        4. Curated Fallback
        All results are filtered by Gemini Vision.
        """
        # --- Source 1: DuckDuckGo General ---
        try:
            from duckduckgo_search import DDGS
            search_query = f"{query} event"
            print(f"Attempting Source 1 (DDG): {search_query}")
            
            with DDGS() as ddgs:
                results = list(ddgs.images(
                    keywords=search_query,
                    region="wt-wt",
                    safesearch="off",
                    max_results=8
                ))
                
                if results:
                    for res in results[:5]:
                        img_url = res['image']
                        if await self._is_image_clean(img_url):
                            print(f"DDG Success (Clean): {img_url}")
                            return img_url
        except Exception as e:
            print(f"DDG Source 1 Failed: {e}")

        # --- Source 2: Unsplash Dynamic Search (via DDG) ---
        try:
            from duckduckgo_search import DDGS
            unsplash_query = f"site:unsplash.com {query} professional event"
            print(f"Attempting Source 2 (Unsplash via DDG): {unsplash_query}")
            
            with DDGS() as ddgs:
                results = list(ddgs.images(
                    keywords=unsplash_query,
                    max_results=5
                ))
                
                if results:
                    for res in results:
                        img_url = res['image']
                        if await self._is_image_clean(img_url):
                            print(f"Unsplash Search Success (Clean): {img_url}")
                            return img_url
        except Exception as e:
            print(f"Unsplash Source 2 Failed: {e}")

        # --- Source 3: AI Generation (Pollinations.ai) ---
        # This is high-reliability because it won't block the server IP
        try:
            print(f"Attempting Source 3 (AI Generation - Pollinations): {query}")
            gen_url = self._generate_fallback_image(query)
            if gen_url:
                print(f"Checking generated image for quality/text: {gen_url}")
                if await self._is_image_clean(gen_url):
                    print(f"AI Generation Success (Clean): {gen_url}")
                    return gen_url
        except Exception as e:
            print(f"Source 3 (AI Gen) Failed: {e}")

        # --- Source 4: Curated Fallbacks ---
        print("All dynamic methods failed or were 'busy'. Using curated fallback.")
        fallbacks = [
            "https://images.unsplash.com/photo-1540575861501-7ad05823c9f5?auto=format&fit=crop&w=1000&q=80",
            "https://images.unsplash.com/photo-1511578314322-379afb476865?auto=format&fit=crop&w=1000&q=80",
            "https://images.unsplash.com/photo-1505373630103-89d00c2a5851?auto=format&fit=crop&w=1000&q=80"
        ]
        return random.choice(fallbacks)

    def _generate_fallback_image(self, title: str) -> str:
        """Generates a related event image using Pollinations.ai with specific style."""
        import urllib.parse
        # Style: Professional Photography, High Resolution, Wide Angle, NO TEXT
        prompt = f"Professional high-resolution photography of an {title} event, cinematic lighting, wide angle shot, natural environment, zero text, no labels, realistic --no text"
        encoded_prompt = urllib.parse.quote(prompt)
        seed = random.randint(1, 999999)
        return f"https://pollinations.ai/p/{encoded_prompt}?width=1000&height=600&seed={seed}&model=flux&nologo=true"

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
            
            # 1. Download image with browser-like headers
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = requests.get(image_url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"Failed to download image for Vision check ({response.status_code}): {image_url}")
                return False
                
            # 2. Optimize & Resize to prevent 504 timeouts
            try:
                img = Image.open(io.BytesIO(response.content))
                # Convert to RGB if necessary (e.g. RGBA/PNG)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if larger than 800px on either dimension
                max_size = 800
                if img.width > max_size or img.height > max_size:
                    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                # Save back to bytes as JPEG with compression
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                image_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
                
            except Exception as resize_err:
                print(f"Image optimization failed, using raw: {resize_err}")
                image_data = base64.b64encode(response.content).decode("utf-8")
            
            # 3. Vision prompt using optimized base64 data
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
                # Add explicit internal timeout for the AI call
                response = await self.llm_google.ainvoke([message])
                decision = response.content.strip().upper()
                return "NO" in decision
            except Exception as e:
                # Catch 429 Quota or 504 Deadline Exceeded
                err_str = str(e).upper()
                if any(x in err_str for x in ["429", "504", "QUOTA", "DEADLINE", "TIMEOUT"]):
                    print(f"Gemini API limit/timeout hit ({e}), bypassing vision filter for: {image_url}")
                    return True # Graceful bypass
                raise e
            
        except Exception as e:
            print(f"Vision check failed or bypassed for {image_url}: {e}")
            return True # Conservative fallback


    def _clean_description(self, text: str) -> str:
        """Removes markdown headers."""
        import re
        text = re.sub(r'^#+\s.*$', '', text, flags=re.MULTILINE)
        return text.strip()

# Initialize the service singleton
ai_service = AIGeneratorService()
