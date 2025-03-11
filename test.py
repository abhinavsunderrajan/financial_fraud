import asyncio
from playwright.async_api import async_playwright

SBR_WS_CDP = f'wss://brd-customer-hl_9c791dfc-zone-scraping_browser4:5jg307dvu5bv@brd.superproxy.io:9222'

async def run(pw):
    print('Connecting to Scraping Browser...')
    browser = await pw.chromium.connect_over_cdp(SBR_WS_CDP)
    try:
        page = await browser.new_page()
        print('Connected! Navigating to webpage')
        await page.goto('https://www.example.com')
        await page.screenshot(path="page.png", full_page=True)
        print("Screenshot saved as 'page.png'")
        html = await page.content()
        print(html)
    finally:
        await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

if __name__ == '__main__':
    asyncio.run(main())