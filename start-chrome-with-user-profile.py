import asyncio
import subprocess
import sys
import tempfile
import json
from pathlib import Path

# Check for required dependencies
try:
    import aiohttp  # type: ignore
    from playwright.async_api import Browser, Page, async_playwright  # type: ignore
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Install with: uv add playwright aiohttp browser-use langchain-openai")
    sys.exit(1)

# Global Playwright instances
playwright_browser: Browser | None = None
playwright_page: Page | None = None


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


async def main():
    print('🚀 FB Marketplace "Sell something" Interaction Script')

    try:
        chrome_process = await start_chrome_with_debug_port()
        cdp_url = "http://localhost:9222"
        await connect_playwright_to_cdp(cdp_url)

        input("Press any key to exit")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if playwright_browser:
            await playwright_browser.close()
        if chrome_process:
            chrome_process.terminate()


if __name__ == "__main__":
    asyncio.run(main())
