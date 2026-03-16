import asyncio
from playwright.async_api import async_playwright
import re

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        print("Navigating...")
        await page.goto('https://udyamregistration.gov.in/UdyamRegistration.aspx')
        html = await page.content()
        inputs = re.findall(r'<input[^>]+>', html)
        for i in inputs:
            if 'aadhaar' in i.lower() or 'aadhar' in i.lower() or 'name' in i.lower():
                print(i)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
