import asyncio
import subprocess
import sys
import tempfile
import json
from pathlib import Path

from pydantic import BaseModel, Field

# Check for required dependencies
try:
    import aiohttp  # type: ignore
    from playwright.async_api import Browser, Page, async_playwright  # type: ignore
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Install with: uv add playwright aiohttp browser-use langchain-openai")
    sys.exit(1)

from browser_use import Agent, BrowserSession, ChatBrowserUse, Tools
from browser_use.agent.views import ActionResult

# Global Playwright instances
playwright_browser: Browser | None = None
playwright_page: Page | None = None


# Custom action parameter models
class PlaywrightClickAction(BaseModel):
    """Parameters for simple Playwright click."""

    selector: str = Field(..., description="CSS selector of the element to click")


class PlaywrightMouseClickAction(BaseModel):
    """Parameters for mouse click via bounding box."""

    selector: str = Field(
        ..., description="CSS selector of the element to click via mouse events"
    )


class PlaywrightCoordinateClickAction(BaseModel):
    """Parameters for clicking at specific coordinates."""

    x: int = Field(..., description="X coordinate to click")
    y: int = Field(..., description="Y coordinate to click")
    description: str = Field(
        ..., description="Description of the element being clicked"
    )


async def start_chrome_with_debug_port(port: int = 9222):
    """Starts Chrome with remote debugging enabled."""
    user_data_dir = tempfile.mkdtemp(prefix="chrome_cdp_")

    chrome_paths = [
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
        "google-chrome",
        "chromium",
    ]

    print("🔍 Searching for Chrome/Chromium executable...")
    chrome_exe = None
    for path in chrome_paths:
        try:
            test_proc = await asyncio.create_subprocess_exec(
                path, "--version", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            await test_proc.wait()
            chrome_exe = path
            print(f"✅ Found Chrome: {chrome_exe}")
            break
        except Exception:
            continue

    if not chrome_exe:
        raise RuntimeError("❌ Chrome/Chromium not found.")

    cmd = [
        chrome_exe,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-extensions",
        "about:blank",
    ]

    print(f"🚀 Starting Chrome with CDP on port {port}...")
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

    print(f"⏳ Waiting for CDP to be ready at http://localhost:{port}/json/version...")
    cdp_ready = False
    for _ in range(20):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"http://localhost:{port}/json/version", timeout=1
                ) as response:
                    if response.status == 200:
                        cdp_ready = True
                        break
        except Exception:
            pass
        await asyncio.sleep(1)

    if not cdp_ready:
        print("❌ CDP failed to become ready within timeout.")
        process.terminate()
        raise RuntimeError("❌ Chrome failed to start with CDP")

    print("✅ Chrome CDP is ready.")
    return process


async def connect_playwright_to_cdp(cdp_url: str):
    """Connects Playwright to the existing Chrome instance and loads auth state."""
    print(f"🔗 Connecting Playwright to CDP at {cdp_url}...")
    global playwright_browser, playwright_page
    pw = await async_playwright().start()
    playwright_browser = await pw.chromium.connect_over_cdp(cdp_url)

    # CDP connection gives us the default context
    context = playwright_browser.contexts[0]

    # Load storage state if it exists
    auth_file = Path("auth.json")
    if auth_file.exists():
        print(f"🔑 Loading authentication state from {auth_file}...")
        with open(auth_file, "r") as f:
            storage_state = json.load(f)

        # Add cookies to the context
        if "cookies" in storage_state:
            await context.add_cookies(storage_state["cookies"])
            print(f"🍪 Added {len(storage_state['cookies'])} cookies.")

        # Local storage needs to be handled per origin on page load or via add_init_script
        if "origins" in storage_state:
            for origin_state in storage_state["origins"]:
                origin = origin_state["origin"]
                ls = origin_state.get("localStorage", [])
                if ls:
                    # Create a script to populate localStorage for this origin
                    ls_script = ";".join(
                        [
                            f"localStorage.setItem({json.dumps(i['name'])}, {json.dumps(i['value'])})"
                            for i in ls
                        ]
                    )
                    await context.add_init_script(
                        f"if (window.location.origin === '{origin}') {{ {ls_script} }}"
                    )
            print(
                f"💾 Prepared localStorage for {len(storage_state['origins'])} origins."
            )
    else:
        print(f"⚠️ {auth_file} not found. Proceeding without saved auth.")

    if context.pages:
        playwright_page = context.pages[0]
    else:
        playwright_page = await context.new_page()

    print("✅ Playwright connected and session state initialized.")


tools = Tools()


@tools.registry.action(
    "Click at specific (x, y) coordinates using Playwright's mouse API. Useful when visual analysis identifies a target location.",
    param_model=PlaywrightCoordinateClickAction,
)
async def playwright_click_coordinates(
    params: PlaywrightCoordinateClickAction, browser_session: BrowserSession
):
    print(
        f"🖱️ Custom Action: Attempting coordinate click at ({params.x}, {params.y}) - {params.description}..."
    )
    try:
        if not playwright_page:
            return ActionResult(error="Playwright not connected.")

        # Perform the click at coordinates
        await playwright_page.mouse.click(params.x, params.y)
        print(f"✅ Successfully clicked coordinates ({params.x}, {params.y})")

        return ActionResult(
            extracted_content=f"Successfully clicked coordinates ({params.x}, {params.y}) for: {params.description}",
            include_in_memory=True,
        )
    except Exception as e:
        return ActionResult(error=f"Playwright coordinate click failed: {str(e)}")


@tools.registry.action(
    "Click a button using Playwright's standard click() method.",
    param_model=PlaywrightClickAction,
)
async def playwright_click_button(
    params: PlaywrightClickAction, browser_session: BrowserSession
):
    print(f"🖱️ Custom Action: Attempting standard click on {params.selector}...")
    try:
        if not playwright_page:
            return ActionResult(error="Playwright not connected.")

        await playwright_page.click(params.selector, timeout=10000)
        print(f"✅ Successfully clicked {params.selector}")
        return ActionResult(
            extracted_content=f"Successfully clicked {params.selector} using .click()",
            include_in_memory=True,
        )
    except Exception as e:
        return ActionResult(error=f"Playwright click failed: {str(e)}")


@tools.registry.action(
    "Click a button by calculating its bounding box and dispatching manual mouse events (mousedown, mouseup, click).",
    param_model=PlaywrightMouseClickAction,
)
async def playwright_mouse_click(
    params: PlaywrightMouseClickAction, browser_session: BrowserSession
):
    print(
        f"🖱️ Custom Action: Attempting native mouse click sequence on {params.selector}..."
    )
    try:
        if not playwright_page:
            return ActionResult(error="Playwright not connected.")

        # Use Playwright's native API for interaction
        element = playwright_page.locator(params.selector).first
        if await element.count() == 0:
            print(f"❌ Element not found: {params.selector}")
            return ActionResult(
                error=f"Element not found with selector: {params.selector}"
            )

        # Ensure visibility and scroll into view
        print("📜 Scrolling element into view...")
        await element.scroll_into_view_if_needed()

        # Get bounding box for the element
        box = await element.bounding_box()
        if not box:
            print("❌ Could not determine bounding box.")
            return ActionResult(
                error="Could not determine bounding box for the element."
            )

        # Calculate center coordinates
        x = box["x"] + box["width"] / 2
        y = box["y"] + box["height"] / 2
        print(f"📍 Target coordinates: ({x}, {y})")

        # Perform manual mouse sequence via Playwright API
        print("🖱️ Moving mouse and performing down/up sequence...")
        await playwright_page.mouse.move(x, y)
        await playwright_page.mouse.down()
        await playwright_page.mouse.up()
        # Optional: native click at the specific point to ensure full propagation
        await playwright_page.mouse.click(x, y)
        print("✅ Native mouse click sequence completed.")

        return ActionResult(
            extracted_content=f"Successfully performed native mouse clicks on {params.selector} at ({x}, {y})",
            include_in_memory=True,
        )

    except Exception as e:
        return ActionResult(error=f"Playwright native mouse click failed: {str(e)}")


async def main():
    print('🚀 FB Marketplace "Sell something" Interaction Script')

    try:
        chrome_process = await start_chrome_with_debug_port()
        cdp_url = "http://localhost:9222"
        await connect_playwright_to_cdp(cdp_url)
        print("🌐 Initializing Browser-Use session...")
        browser_session = BrowserSession(cdp_url=cdp_url)

        print("🤖 Initializing AI Agent...")
        agent = Agent(
            task="""
            1. Navigate to https://www.facebook.com/groups/autooglasinis
            2. Visually identify the 'Sell something' button in the screenshot.
            3. Use the 'playwright_click_coordinates' tool to click the center of that button using its (x, y) coordinates.
            4. If visual identification is difficult, fall back to 'playwright_click_button' with selector 'text="Sell Something"'.
            5. Confirm if the 'Create new listing' dialog or similar appeared.
            """,
            llm=ChatBrowserUse(),
            tools=tools,
            browser_session=browser_session,
        )

        print("🎯 Starting agent...")
        result = await agent.run()
        print(f"✅ Result: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if playwright_browser:
            await playwright_browser.close()
        if chrome_process:
            chrome_process.terminate()


if __name__ == "__main__":
    asyncio.run(main())
