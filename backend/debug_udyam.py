import asyncio
from playwright.async_api import async_playwright

async def debug_udyam():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to Udyam...")
        await page.goto('https://udyamregistration.gov.in/UdyamRegistration.aspx', wait_until='networkidle')
        await page.wait_for_timeout(5000) # Give extra time for JS to render
        
        # Take screenshot and save DOM
        await page.screenshot(path='udyam_debug.png')
        print("Screenshot saved to udyam_debug.png")
        
        # Dump input fields
        inputs = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('input')).map(i => ({
                id: i.id,
                name: i.name,
                type: i.type,
                placeholder: i.placeholder,
                isVisible: i.offsetParent !== null
            }));
        }''')
        
        print(f"Found {len(inputs)} input fields:")
        for i in inputs:
            if 'aadhar' in (i.get('id', '').lower() or '') or 'name' in (i.get('id', '').lower() or '') or 'aadhar' in (i.get('name', '').lower() or '') or 'name' in (i.get('name', '').lower() or ''):
                print(i)
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_udyam())
