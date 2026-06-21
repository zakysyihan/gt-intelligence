"""Visual verification script for GT Intelligence UI.

Uses Playwright to screenshot the running app and evaluate:
1. Dashboard loads with all 8 widgets
2. Chat panel opens/closes
3. All charts render
4. Responsive layout works

Run: python tests/visual_verify.py
Output: tests/screenshots/ directory with PNG files
"""

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

BASE_URL = "http://43.133.140.154:8000"
SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


async def take_screenshots():
    SCREENSHOT_DIR.mkdir(exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1440, "height": 900})

        # 1. Dashboard loads
        print("1. Loading dashboard...")
        await page.goto(BASE_URL)
        await page.wait_for_timeout(4000)  # Wait for charts to render
        await page.screenshot(path=str(SCREENSHOT_DIR / "01_dashboard.png"), full_page=False)
        print("   ✅ Dashboard screenshot saved")

        # 2. Check metrics are rendered
        metrics = await page.query_selector_all(".metric-card")
        print(f"   Metrics rendered: {len(metrics)} cards")

        # 3. Check charts are rendered
        charts = await page.evaluate("""
            () => {
                const ids = ['chart-subcategory', 'chart-price', 'chart-geo',
                             'chart-quadrant', 'chart-revenue'];
                return ids.map(id => {
                    const el = document.getElementById(id);
                    return {
                        id,
                        hasContent: el ? el.children.length > 0 : false,
                        hasPlotly: el ? el.querySelector('.plotly') !== null : false
                    };
                });
            }
        """)
        for c in charts:
            status = "✅" if c["hasPlotly"] else "⚠️"
            print(f"   {status} Chart {c['id']}: rendered={c['hasPlotly']}")

        # 4. Open chat panel
        print("\n2. Opening chat panel...")
        toggle = await page.query_selector("#chat-toggle")
        if toggle:
            await toggle.click()
            await page.wait_for_timeout(1000)
            await page.screenshot(path=str(SCREENSHOT_DIR / "02_chat_open.png"), full_page=False)
            print("   ✅ Chat open screenshot saved")

        # 5. Check chat panel is visible
        chat_panel = await page.query_selector("#chat-panel")
        if chat_panel:
            visible = await chat_panel.is_visible()
            print(f"   Chat panel visible: {visible}")

        # 6. Send a test message
        print("\n3. Sending test message...")
        chat_input = await page.query_selector("#chat-input")
        if chat_input:
            await chat_input.fill("Top 3 produk terlaris?")
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(8000)  # Wait for agent response
            await page.screenshot(path=str(SCREENSHOT_DIR / "03_chat_response.png"), full_page=False)
            print("   ✅ Chat response screenshot saved")

        # 7. Check if response rendered
        messages = await page.query_selector_all(".msg")
        print(f"   Messages rendered: {len(messages)}")

        # 8. Toggle chat closed
        print("\n4. Closing chat panel...")
        toggle = await page.query_selector("#chat-toggle")
        if toggle:
            await toggle.click()
            await page.wait_for_timeout(1000)
            await page.screenshot(path=str(SCREENSHOT_DIR / "04_chat_closed.png"), full_page=False)
            print("   ✅ Chat closed screenshot saved")

        # 9. Responsive test (mobile)
        print("\n5. Testing responsive layout...")
        await page.set_viewport_size({"width": 375, "height": 812})
        await page.wait_for_timeout(1000)
        await page.screenshot(path=str(SCREENSHOT_DIR / "05_mobile.png"), full_page=False)
        print("   ✅ Mobile screenshot saved")

        await browser.close()
        print(f"\n✅ All screenshots saved to {SCREENSHOT_DIR}/")


if __name__ == "__main__":
    asyncio.run(take_screenshots())
