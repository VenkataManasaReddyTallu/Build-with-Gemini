import asyncio
import os
import shutil
from playwright.async_api import async_playwright

CLOUD_RUN_URL = "https://sous-chef-frontend-736273604606.us-central1.run.app"
ARTIFACT_DIR = "/config/.gemini/antigravity/brain/0a686dfc-a0f2-4d4e-9a40-6f3ad3c50616"
OUTPUT_VIDEO_PATH = os.path.join(ARTIFACT_DIR, "sous_chef_demo.webm")

async def record():
    temp_video_dir = os.path.join(ARTIFACT_DIR, "scratch", "video_temp")
    os.makedirs(temp_video_dir, exist_ok=True)

    async with async_playwright() as p:
        # Launch browser in headless mode
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            record_video_dir=temp_video_dir,
            record_video_size={"width": 1280, "height": 800}
        )
        page = await context.new_page()

        print("Navigating to Cloud Run App:", CLOUD_RUN_URL)
        await page.goto(CLOUD_RUN_URL, wait_until="networkidle")
        await asyncio.sleep(2)

        # ---------------------------------------------------------------------
        # Turn 1: Primary App Feature (Database lookup for recipes in cookbook)
        # ---------------------------------------------------------------------
        print("Executing Turn 1: Cookbook Recipes...")
        prompt_1 = "List recipes in my cookbook"
        await page.fill("#input", prompt_1)
        await asyncio.sleep(1)
        await page.click("button[type='submit']")

        # Wait for agent bubble to contain rendered A2UI card
        await page.wait_for_selector(".msg.agent .a2card", timeout=45000)
        print("Turn 1 complete! A2UI card received.")
        await asyncio.sleep(5)

        # ---------------------------------------------------------------------
        # Turn 2: Richer prompt with Tool Call & Image Generation
        # ---------------------------------------------------------------------
        print("Executing Turn 2: Generate Dish Photo Tool Call...")
        prompt_2 = "Generate a presentation photo for Lemon Herb Salmon and save it"
        await page.fill("#input", prompt_2)
        await asyncio.sleep(1)
        await page.click("button[type='submit']")

        # Wait for second agent reply (Image card or response card)
        # The agent returns an A2UI card with Image component or confirmation
        await asyncio.sleep(25)
        print("Turn 2 complete!")
        await asyncio.sleep(5)

        # Get recorded video path before closing
        video_page = page.video
        await page.close()
        await context.close()
        await browser.close()

        saved_path = await video_page.path()
        print(f"Recorded video temp path: {saved_path}")
        shutil.copy(saved_path, OUTPUT_VIDEO_PATH)
        print(f"Successfully saved final video to: {OUTPUT_VIDEO_PATH}")

if __name__ == "__main__":
    asyncio.run(record())
