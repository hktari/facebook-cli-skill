"""
Custom Tools Example

This example demonstrates how to create custom tools that the agent can use
alongside the built-in browser actions.
"""

import asyncio

from dotenv import load_dotenv

from browser_use import ActionResult, Agent, Browser, ChatBrowserUse, Tools

load_dotenv()

# Create a Tools instance to register custom actions
tools = Tools()


@tools.registry.action("Save text content to a file")
async def save_to_file(filename: str, content: str):
    from pathlib import Path

    try:
        Path(filename).write_text(content, encoding="utf-8")
        return ActionResult(
            extracted_content=f"Saved to {filename}", include_in_memory=True
        )
    except Exception as e:
        return ActionResult(
            extracted_content=f"Error saving file: {e}", include_in_memory=True
        )


async def main():
    browser = Browser.from_system_chrome()
    llm = ChatBrowserUse()
    task = """
    go to: https://www.facebook.com/groups/autooglasinis and create a post. 
    
    Additional information:
    =====
    - use serbo-croatian texts
    - use marketing image at /home/bostjan/source/autocare-ai-agent/assets/marketing_post_image.png
    =====

    Follow the steps to create a post:
    =====
  - Click on "Sell Something"
  - Click on "Item for sale"
  - Click on "Add photos" 
    - attach marketing image
  - set title: 
    - SLO
      - Preprost izračun ter primerjava cen velikega ter malega servis
    - SERBO-CROATIAN
      - Jednostavan izračun i poređenje cijena velikog i malog servisa.
  - set price: 1
  - set condition: "New"
  - expand section "More Details" by clicking on it
  - add description: 
    - SLO
      - Živjo vsem! Z kolegom razvijava spletno stran, ki bi omogočila hiter izračun cene za mali in veliki servis, ter pomagala najti dobrega mehanika v bližini. Prej kot zadevo dokončava, naju zanima, ali bi vam to sploh prišlo prav? Vsak komentar pomaga! Pustim link do testne strani, da si lažje predstavljate:
      - https://autocare-ai-landing-page.vercel.app/sl
        - **URL**: https://autocare-ai-landing-page.vercel.app/sl"
    - SERBO-CROATIAN
      - Zdravo svima! Sa kolegom razvijam web stranicu koja bi omogućila brz izračun cijene za mali i veliki servis, te pomogla pronaći dobrog mehaničara u blizini. Prije nego što završimo, zanima nas da li bi vam ovo uopšte bilo od koristi? Svaki komentar je dobrodošao! Ostavljam link do testne stranice da lakše vidite o čemu se radi: 
      - https://autocare-ai-landing-page.vercel.app/hr
        - **URL**: https://autocare-ai-landing-page.vercel.app/hr"
  - set location: 
    - Ljubljana (if Slovenian post)
    - Zagreb (if Croatian post)
    - Beograd (if Bosnian post)
  - click "Next"
  - click "Post"
  - "Listing published" popup is displayed
  - task completed
    =====
    """
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
        tools=tools,
    )

    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
