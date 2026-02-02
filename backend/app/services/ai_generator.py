from typing import List, Dict, Any, Optional
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

import urllib.parse

# Define the expected output structure
class AgendaItem(BaseModel):
    startTime: str = Field(description="Start time in HH:MM format (24h)")
    endTime: str = Field(description="End time in HH:MM format (24h)")
    title: str = Field(description="Title of the session")
    description: str = Field(description="Brief description of the session")

class SpeakerItem(BaseModel):
    name: str = Field(description="Name of the speaker")
    role: str = Field(description="Role or job title of the speaker")
    company: str = Field(description="Company or organization of the speaker")

class EventContent(BaseModel):
    description: str = Field(description="A compelling, markdown-formatted event description (2-3 paragraphs). DO NOT use hashtags.")
    agenda: List[AgendaItem] = Field(description="A suggested agenda with 3-5 items")
    speakers: List[SpeakerItem] = Field(description="3 hypothetical speakers relevant to the event theme")
    image_prompt: str = Field(description="A detailed, visual description of a cover image for this event (e.g., 'futuristic conference hall with neon lights', 'minimalist workshop setting with plants').")
    tags: List[str] = Field(description="5 relevant tags for the event")

class AIGeneratorService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            print("WARNING: GROQ_API_KEY not found in environment variables.")
        
        # Initialize Groq Chat Model
        self.llm = ChatGroq(
            temperature=0.7,
            groq_api_key=self.api_key,
            model_name="llama-3.3-70b-versatile"
        )
        
        self.parser = JsonOutputParser(pydantic_object=EventContent)

    async def generate_event_content(self, title: str, category: str, start_time: str, end_time: str) -> Dict[str, Any]:
        """
        Generates description, agenda, and image keywords for an event.
        """
        if not self.api_key:
            raise Exception("GROQ_API_KEY is missing. Please add it to your .env file.")

        # Calculate dynamic schedule
        total_sessions, schedule_str = self._calculate_schedule(start_time, end_time)

        # detailed prompt
        system_prompt = f"""You are an expert event planner. Generate content for: "{{title}}" (Category: "{{category}}").

        STRICT OUTPUT REQUIREMENTS:
        1. Description: Compelling, 2 paragraphs, NO markdown/hashtags.
        2. Agenda: Generate EXACTLY {total_sessions} continuous agenda sessions.
           - TIME WINDOW: {start_time} to {end_time}
           - SESSION DURATION: 45 minutes generally (Back-to-back, NO breaks).
           - RULE: The last session must end EXACTLY at {end_time} (adjust its duration if needed).
           - STRICT START TIMES: {schedule_str}
           - RULE: The first session MUST start at {start_time}.
        3. Speakers: 3 realistic names/roles.
        4. Tags: 5 relevant tags.
        5. Image Prompt: A highly descriptive visual prompt for an AI image generator. Describe the scene, lighting, and mood.

        Respond ONLY in valid JSON."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "Title: {title}\nCategory: {category}\n\n{format_instructions}")
        ])

        chain = prompt | self.llm | self.parser

        try:
            result = await chain.ainvoke({
                "title": title, 
                "category": category,
                "start_time": start_time,
                "end_time": end_time,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            # Clean description to remove markdown headers
            if "description" in result:
                result["description"] = self._clean_description(result["description"])

            # Generate Pollinations URL from image prompt
            if "image_prompt" in result:
                encoded_prompt = urllib.parse.quote(result["image_prompt"])
                # Using Pollinations.ai with Flux model (default or specified)
                # Adding seed for consistency if needed, but random is fine for variety
                result["imageUrl"] = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&model=flux&nologo=true"
            else:
                # Fallback
                result["imageUrl"] = "https://source.unsplash.com/1600x900/?conference"
            
            return result
            
        except Exception as e:
            print(f"Error generating content: {e}")
            raise e

    def _clean_description(self, text: str) -> str:
        """Removes markdown headers and formatting characters to ensure plain text."""
        import re
        # Remove markdown headers
        text = re.sub(r'(?m)^#+\s*', '', text)
        # Remove bold/italic markers (* and _)
        text = re.sub(r'[\*_`]', '', text)
        # Remove link syntax [text](url) -> text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        return text.strip()

    def _calculate_schedule(self, start_str: str, end_str: str):
        """Calculates start times to fill the duration, handling remainders."""
        from datetime import datetime, timedelta

        # Parse times
        base_date = "2026-01-01"
        start = datetime.strptime(f"{base_date} {start_str}", "%Y-%m-%d %H:%M")
        end = datetime.strptime(f"{base_date} {end_str}", "%Y-%m-%d %H:%M")

        duration = end - start
        total_minutes = duration.total_seconds() / 60
        
        # Calculate full 45-min sessions
        full_sessions = int(total_minutes // 45)
        remainder = total_minutes % 45
        
        # If there's a significant gap (e.g. > 15 mins), add a final short session
        total_sessions = full_sessions + (1 if remainder >= 15 else 0)
        
        start_times = []
        current = start
        for _ in range(total_sessions):
            start_times.append(current.strftime("%H:%M"))
            current += timedelta(minutes=45)
            
        return total_sessions, ", ".join(start_times)

# Singleton instance
ai_service = AIGeneratorService()
