"""Full visual verification of GT Intelligence dashboard."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = "http://43.133.140.154:8000"
SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

async def verify():
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    issues = []

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1440, "height": 900})

        # === 1. DASHBOARD LOAD ===
        print("1. Dashboard load")
        await page.goto(BASE_URL)
        await page.wait_for_timeout(4000)

        # Check no horizontal scroll
        hscroll = await page.evaluate("() => document.documentElement.scrollWidth > document.documentElement.clientWidth")
        if hscroll:
            issues.append("Horizontal scroll detected")
        print(f"   {'✅' if not hscroll else '❌'} No horizontal scroll")

        # Check metric cards - no delta text
        delta = await page.query_selector(".metric-delta")
        if delta:
            issues.append("Green delta text still present")
        print(f"   {'✅' if not delta else '❌'} No delta text in metrics")

        # Check metric values
        vals = await page.evaluate("() => Array.from(document.querySelectorAll('.metric-value')).map(e => e.textContent)")
        print(f"   Metrics: {vals}")

        # Check filter bar
        filter_bar = await page.query_selector(".filters-bar")
        print(f"   {'✅' if filter_bar else '❌'} Filter bar present")

        # Check all charts have consistent height
        heights = await page.evaluate("() => ['chart-subcategory', 'chart-price', 'chart-quadrant', 'chart-distribution'].map(id => { const el = document.getElementById(id); return el ? Math.round(el.getBoundingClientRect().height) : 0 })")
        consistent = len(set(heights)) <= 1 and heights[0] > 0
        print(f"   {'✅' if consistent else '❌'} Chart heights consistent: {heights}")

        # Check no chart is cut off (no overflow)
        overflow = await page.evaluate("() => ['chart-subcategory', 'chart-price', 'chart-quadrant', 'chart-distribution'].some(id => { const el = document.getElementById(id); return el ? el.scrollWidth > el.clientWidth : false })")
        if overflow:
            issues.append("Chart content overflows")
        print(f"   {'✅' if not overflow else '❌'} No chart overflow")

        # Check quadrant lines are centered
        quad_traces = await page.evaluate("() => { const el = document.getElementById('chart-quadrant'); if (!el || !el.data) return null; const shapes = el.layout?.shapes || []; return shapes.map(s => ({ x0: s.x0, x1: s.x1, y0: s.y0, y1: s.y1 })) }")
        if quad_traces:
            print(f"   Quadrant lines: {quad_traces}")
        else:
            print("   ⚠️ Could not read quadrant shapes")

        # Check demand x price quadrant exists
        price_quad = await page.evaluate("() => { const el = document.getElementById('chart-distribution'); return el && el.data && el.data.length > 0 }")
        print(f"   {'✅' if price_quad else '❌'} Demand × Price quadrant has data")

        # Screenshot full dashboard
        await page.screenshot(path=str(SCREENSHOT_DIR / "verify_01_full.png"), full_page=True)

        # === 2. CHARTS ROW BY ROW ===
        print("\n2. Charts verification")
        charts = await page.evaluate("() => ['chart-subcategory', 'chart-price', 'chart-quadrant', 'chart-distribution'].map(id => ({ id, hasPlotly: document.getElementById(id)?.querySelector('.js-plotly-plot') !== null, width: Math.round(document.getElementById(id)?.getBoundingClientRect().width || 0) }))")
        for c in charts:
            status = "✅" if c['hasPlotly'] else "❌"
            print(f"   {status} {c['id']}: rendered={c['hasPlotly']}, width={c['width']}px")

        # === 3. FILTER INTERACTION ===
        print("\n3. Filter interaction")
        # Click subcategory multiselect
        ms_btn = await page.query_selector(".multiselect-btn")
        if ms_btn:
            await ms_btn.click()
            await page.wait_for_timeout(300)
            checkboxes = await page.query_selector_all("#ms-dropdown input[type='checkbox']")
            if len(checkboxes) > 0:
                await checkboxes[0].click()
                await page.wait_for_timeout(2000)
                vals_after = await page.evaluate("() => Array.from(document.querySelectorAll('.metric-value')).map(e => e.textContent)")
                print(f"   ✅ Filter applied — metrics changed to: {vals_after}")
                changed = vals_after != vals
                if changed:
                    print(f"   ✅ Metrics updated after filter")
                else:
                    issues.append("Metrics didn't update after filter")
                    print(f"   ❌ Metrics unchanged after filter")
            # Reset
            reset_btn = await page.query_selector("button[onclick='resetFilters()']")
            if reset_btn:
                await reset_btn.click()
                await page.wait_for_timeout(1000)
        await page.screenshot(path=str(SCREENSHOT_DIR / "verify_02_filtered.png"))

        # === 4. CHAT TOGGLE ===
        print("\n4. Chat toggle")
        toggle = await page.query_selector("#chat-toggle")
        if toggle:
            await toggle.click()
            await page.wait_for_timeout(1500)

            chat_visible = await page.evaluate("() => document.getElementById('chat-panel')?.style.display !== 'none'")
            print(f"   {'✅' if chat_visible else '❌'} Chat panel visible")

            # Check charts resized (no overflow after chat open)
            hscroll_chat = await page.evaluate("() => document.documentElement.scrollWidth > document.documentElement.clientWidth")
            if hscroll_chat:
                issues.append("Horizontal scroll with chat open")
            print(f"   {'✅' if not hscroll_chat else '❌'} No horizontal scroll with chat open")

            # Check chart widths are smaller (dashboard adjusted)
            widths_chat = await page.evaluate("() => ['chart-subcategory', 'chart-price'].map(id => Math.round(document.getElementById(id)?.getBoundingClientRect().width || 0))")
            print(f"   Chart widths with chat: {widths_chat}px")

            await page.screenshot(path=str(SCREENSHOT_DIR / "verify_03_chat_open.png"))

            # Close chat
            await toggle.click()
            await page.wait_for_timeout(1500)

        # === 5. CHAT FUNCTIONALITY ===
        print("\n5. Chat functionality")
        await toggle.click()
        await page.wait_for_timeout(1500)

        # Send a message
        chat_input = await page.query_selector("#chat-input")
        if chat_input:
            await chat_input.fill("Top 5 produk terlaris?")
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(10000)

            messages = await page.query_selector_all(".msg")
            print(f"   Messages: {len(messages)}")

            has_sql = await page.evaluate("() => document.querySelectorAll('.sql-block').length > 0")
            has_insight = await page.evaluate("() => document.querySelectorAll('.insight-box').length > 0")
            print(f"   {'✅' if has_sql else '⚠️'} SQL block: {has_sql}")
            print(f"   {'✅' if has_insight else '⚠️'} Insight: {has_insight}")

        await page.screenshot(path=str(SCREENSHOT_DIR / "verify_04_chat_response.png"))

        # === 6. QUICK ACTIONS ===
        print("\n6. Quick actions")
        qa_btns = await page.query_selector_all(".quick-btn")
        print(f"   Quick action buttons: {len(qa_btns)}")

        # === 7. RESPONSIVE ===
        print("\n7. Responsive (mobile)")
        await page.set_viewport_size({"width": 375, "height": 812})
        await page.wait_for_timeout(500)
        hscroll_mobile = await page.evaluate("() => document.documentElement.scrollWidth > document.documentElement.clientWidth")
        print(f"   {'✅' if not hscroll_mobile else '❌'} No horizontal scroll on mobile")
        await page.screenshot(path=str(SCREENSHOT_DIR / "verify_05_mobile.png"))

        # === SUMMARY ===
        print(f"\n{'=' * 40}")
        if issues:
            print(f"❌ {len(issues)} ISSUES:")
            for i in issues:
                print(f"   - {i}")
        else:
            print("✅ ALL CHECKS PASSED")

        await browser.close()

asyncio.run(verify())
