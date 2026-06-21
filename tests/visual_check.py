"""Thorough visual verification of GT Intelligence UI.

Tests all requirements using Playwright browser automation.
Checks: layout, charts, chat, toggle, scroll issues, responsive.
"""

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

BASE_URL = "http://43.133.140.154:8000"
SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


async def check():
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    issues = []

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1440, "height": 900})

        # === 1. DASHBOARD LOAD ===
        print("=" * 60)
        print("1. DASHBOARD LOAD")
        print("=" * 60)
        await page.goto(BASE_URL)
        await page.wait_for_timeout(5000)

        # Check horizontal scroll
        has_hscroll = await page.evaluate("""
            () => document.documentElement.scrollWidth > document.documentElement.clientWidth
        """)
        if has_hscroll:
            scroll_width = await page.evaluate("() => document.documentElement.scrollWidth")
            client_width = await page.evaluate("() => document.documentElement.clientWidth")
            issues.append(f"HORIZONTAL SCROLL: scrollWidth={scroll_width} > clientWidth={client_width}")
            print(f"   ❌ Horizontal scroll detected: {scroll_width}px > {client_width}px")
        else:
            print("   ✅ No horizontal scroll")

        # Check all 8 widget containers exist
        widgets = {
            "metrics": "#metrics-grid",
            "subcategory": "#chart-subcategory",
            "price": "#chart-price",
            "geo": "#chart-geo",
            "quadrant": "#chart-quadrant",
            "revenue": "#chart-revenue",
            "specs": "#chart-specs",
        }
        for name, sel in widgets.items():
            el = await page.query_selector(sel)
            if el:
                visible = await el.is_visible()
                has_children = await page.evaluate(f"() => document.querySelector('{sel}')?.children.length > 0")
                status = "✅" if visible and has_children else "⚠️"
                print(f"   {status} Widget '{name}': visible={visible}, hasContent={has_children}")
                if not visible or not has_children:
                    issues.append(f"Widget '{name}' missing or empty")
            else:
                print(f"   ❌ Widget '{name}' not found")
                issues.append(f"Widget '{name}' DOM element not found")

        # Check metric cards content
        metric_values = await page.evaluate("""
            () => Array.from(document.querySelectorAll('.metric-value')).map(el => el.textContent)
        """)
        print(f"   Metric values: {metric_values}")

        await page.screenshot(path=str(SCREENSHOT_DIR / "check_01_dashboard.png"))

        # === 2. CHART INTERACTIVITY ===
        print("\n" + "=" * 60)
        print("2. CHART INTERACTIVITY")
        print("=" * 60)

        # Check Plotly charts have traces
        plotly_count = await page.evaluate("""
            () => document.querySelectorAll('.js-plotly-plot').length
        """)
        print(f"   Plotly charts rendered: {plotly_count}")
        if plotly_count < 5:
            issues.append(f"Only {plotly_count} Plotly charts rendered (expected 5+)")

        # === 3. CHAT TOGGLE ===
        print("\n" + "=" * 60)
        print("3. CHAT TOGGLE")
        print("=" * 60)

        # Open chat
        toggle = await page.query_selector("#chat-toggle")
        toggle_text = await toggle.inner_text()
        print(f"   Initial toggle text: '{toggle_text}'")
        await toggle.click()
        await page.wait_for_timeout(1000)

        chat_panel = await page.query_selector("#chat-panel")
        chat_visible = await chat_panel.is_visible() if chat_panel else False
        print(f"   Chat panel visible after open: {chat_visible}")
        if not chat_visible:
            issues.append("Chat panel not visible after clicking toggle")

        toggle_text = await toggle.inner_text()
        print(f"   Toggle text after open: '{toggle_text}'")

        # Check for horizontal scroll after chat opens
        has_hscroll_chat = await page.evaluate("""
            () => document.documentElement.scrollWidth > document.documentElement.clientWidth
        """)
        if has_hscroll_chat:
            issues.append("Horizontal scroll when chat is open")
            print("   ❌ Horizontal scroll with chat open")
        else:
            print("   ✅ No horizontal scroll with chat open")

        await page.screenshot(path=str(SCREENSHOT_DIR / "check_02_chat_open.png"))

        # === 4. CHAT FUNCTIONALITY ===
        print("\n" + "=" * 60)
        print("4. CHAT FUNCTIONALITY")
        print("=" * 60)

        # Check quick actions exist
        quick_btns = await page.query_selector_all(".quick-btn")
        print(f"   Quick action buttons: {len(quick_btns)}")
        if len(quick_btns) < 6:
            issues.append(f"Only {len(quick_btns)} quick action buttons (expected 6)")

        # Check session selector
        session_select = await page.query_selector("#session-select")
        if session_select:
            options = await page.evaluate("""
                () => Array.from(document.querySelectorAll('#session-select option')).map(o => o.textContent)
            """)
            print(f"   Sessions: {options}")

        # Send a message
        chat_input = await page.query_selector("#chat-input")
        if chat_input:
            await chat_input.fill("Produk apa yang paling murah tapi laris?")
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(10000)  # Wait for agent response

            messages = await page.query_selector_all(".msg")
            print(f"   Messages after send: {len(messages)}")

            # Check if response has SQL, table, insight
            has_sql = await page.evaluate("""
                () => document.querySelectorAll('.sql-block').length > 0
            """)
            has_table = await page.evaluate("""
                () => document.querySelectorAll('.data-table').length > 0
            """)
            has_insight = await page.evaluate("""
                () => document.querySelectorAll('.insight-box').length > 0
            """)
            print(f"   Response has SQL: {has_sql}")
            print(f"   Response has table: {has_table}")
            print(f"   Response has insight: {has_insight}")

            if not has_sql:
                issues.append("Chat response missing SQL block")
            if not has_insight:
                issues.append("Chat response missing insight")

        await page.screenshot(path=str(SCREENSHOT_DIR / "check_03_chat_response.png"))

        # === 5. CLOSE CHAT ===
        print("\n" + "=" * 60)
        print("5. CLOSE CHAT")
        print("=" * 60)

        toggle = await page.query_selector("#chat-toggle")
        await toggle.click()
        await page.wait_for_timeout(1000)

        chat_visible = await chat_panel.is_visible() if chat_panel else False
        print(f"   Chat panel visible after close: {chat_visible}")

        # Check no horizontal scroll
        has_hscroll_closed = await page.evaluate("""
            () => document.documentElement.scrollWidth > document.documentElement.clientWidth
        """)
        if has_hscroll_closed:
            issues.append("Horizontal scroll after chat closed")
        else:
            print("   ✅ No horizontal scroll after close")

        await page.screenshot(path=str(SCREENSHOT_DIR / "check_04_closed.png"))

        # === 6. SCROLLABLE DASHBOARD CONTENT ===
        print("\n" + "=" * 60)
        print("6. SCROLLABLE DASHBOARD")
        print("=" * 60)

        # Scroll down to see more widgets
        await page.evaluate("() => document.querySelector('.dashboard-panel')?.scrollTo(0, 9999)")
        await page.wait_for_timeout(500)
        await page.screenshot(path=str(SCREENSHOT_DIR / "check_05_scrolled.png"))

        # Check if specs table rendered
        specs_content = await page.evaluate("""
            () => {
                const el = document.getElementById('chart-specs');
                return el ? el.innerHTML.length : 0;
            }
        """)
        print(f"   Specs widget content length: {specs_content}")
        if specs_content < 50:
            issues.append("Specs widget may be empty or minimal")

        # === SUMMARY ===
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        if issues:
            print(f"❌ {len(issues)} ISSUES FOUND:")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
        else:
            print("✅ ALL CHECKS PASSED")

        await browser.close()
        return issues


if __name__ == "__main__":
    result = asyncio.run(check())
