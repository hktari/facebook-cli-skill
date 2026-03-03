import asyncio

from browser_use import Browser


async def export_auth():
    browser = Browser.from_system_chrome()
    await browser.start()
    await browser.export_storage_state("auth.json")
    await browser.stop()


if __name__ == "__main__":
    asyncio.run(export_auth())
