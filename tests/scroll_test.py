"""Test horizontal scroll at various viewport widths."""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = "http://43.133.140.154:8000"
SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

async def test():
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        for width in [1920, 1440, 1280, 1024]:
            page = await browser.new_page(viewport={"width": width, "height": 900})
            await page.goto(BASE_URL)
            await page.wait_for_timeout(4000)

            hscroll = await page.evaluate("""
                () => ({
                    scrollWidth: document.documentElement.scrollWidth,
                    clientWidth: document.documentElement.clientWidth,
                    overflows: document.documentElement.scrollWidth > document.documentElement.clientWidth,
                    bodyOverflow: document.body.scrollWidth > document.body.clientWidth,
                })
            """)

            status = "❌ SCROLL" if hscroll['overflows'] else "✅"
            print(f"{status} {width}px: scrollWidth={hscroll['scrollWidth']}, clientWidth={hscroll['clientWidth']}")

            await page.screenshot(path=str(SCREENSHOT_DIR / f"scroll_{width}.png"))
            await page.close()

        # Also test with chat open
        page = await browser.new_page(viewport={"width": 1280, "height": 900})
        await page.goto(BASE_URL)
        await page.wait_for_timeout(4000)
        await page.click("#chat-toggle")
        await page.wait_for_timeout(1000)

        hscroll = await page.evaluate("""
            () => ({
                scrollWidth: document.documentElement.scrollWidth,
                clientWidth: document.documentElement.clientWidth,
                overflows: document.documentElement.scrollWidth > document.documentElement.clientWidth,
            })
        """)
        status = "❌ SCROLL" if hscroll['overflows'] else "✅"
        print(f"{status} 1280px + chat: scrollWidth={hscroll['scrollWidth']}, clientWidth={hscroll['clientWidth']}")
        await page.screenshot(path=str(SCREENSHOT_DIR / "scroll_1280_chat.png"))

        await browser.close()

asyncio.run(test())
