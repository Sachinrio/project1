
import asyncio
import os
from app.services.ai_generator import ai_service

async def test_ai():
    print("Testing AI Generation...")
    try:
        result = await ai_service.generate_event_content(
            title="Tech Conference 2026",
            category="Technology",
            start_time="09:00",
            end_time="17:00"
        )
        print("Result received:")
        import json
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ai())
