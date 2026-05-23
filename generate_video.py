import os
import time
import requests
import random
from playwright.sync_api import sync_playwright

def get_ai_prompt():
    themes = [
        "First-person drone POV, massive golden sand dunes, Sahara desert, 8k, unreal engine 5, cinematic",
        "1700s cobblestone street, old European town, morning mist, flickering lanterns, hyper-realistic",
        "Cinematic cozy cabin, heavy rain against windows, dark pine forest, lightning, volumetric lighting",
        "Underwater POV, tropical coral reef, sun rays piercing through blue water, cinematic 4k"
    ]
    api_key = os.getenv("OPENROUTER_API_KEY")
    theme = random.choice(themes)
    try:
        headers = {"Authorization": f"Bearer {api_key}", "HTTP-Referer": "https://github.com/"}
        data = {
            "model": "meta-llama/llama-3-8b-instruct:free",
            "messages": [{"role": "user", "content": f"Create a 1-sentence mind-blowing AI video prompt for: {theme}. Use 9:16 aspect ratio."}]
        }
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=15)
        return res.json()['choices'][0]['message']['content']
    except: return theme

def run_automation():
    prompt = get_ai_prompt()
    filename = f"video_{int(time.time())}.mp4"
    print(f"🚀 Prompt: {prompt}")

    with sync_playwright() as p:
        # Launching with specific arguments to bypass bot detection
        browser = p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        context = browser.new_context(viewport={'width': 1600, 'height': 900})
        
        cookie_value = os.getenv("LEONARDO_COOKIE")
        context.add_cookies([{
            'name': '__Secure-better-auth.session_token',
            'value': cookie_value,
            'domain': 'app.leonardo.ai',
            'path': '/',
            'secure': True,
            'httpOnly': True,
            'sameSite': 'Lax'
        }])

        page = context.new_page()
        
        try:
            print("🌐 Navigating to Leonardo...")
            page.goto("https://app.leonardo.ai/ai-generations", wait_until="networkidle", timeout=9000000)
            time.sleep(20)

            # 1. Enter Prompt
            print("✍️ Entering Prompt...")
            # We use a very aggressive search for the textarea
            page.wait_for_selector("textarea", timeout=60000)
            textarea = page.locator("textarea").first
            textarea.fill(prompt)
            time.sleep(2)

            # 2. Start Generation
            print("🎬 Clicking Generate...")
            page.keyboard.press("Enter")
            
            # 3. Wait for Video to Generate
            print("⏳ Video is being created by AI. Waiting 5 minutes...")
            time.sleep(300) 

            # 4. Attempt to Download the Video
            print("💾 Searching for the video file to download...")
            # We look for the most recent video download button
            page.reload()
            time.sleep(15)
            
            # Find all video elements and get the first one's source
            video_tags = page.locator("video")
            if video_tags.count() > 0:
                video_url = video_tags.first.get_attribute("src")
                if video_url and "blob" not in video_url:
                    print(f"📥 Downloading video from: {video_url}")
                    r = requests.get(video_url)
                    with open(filename, 'wb') as f:
                        f.write(r.content)
                    print(f"✅ Video saved as {filename}")
                else:
                    print("⚠️ Found a video player but couldn't get the direct link.")
            else:
                print("❌ No video elements found on page.")

            # Record in Log
            with open("daily_log.md", "a") as f:
                f.write(f"\n- {time.ctime()}: Generated {filename} | Prompt: {prompt}")

        except Exception as e:
            print(f"❌ Critical Error: {e}")
            page.screenshot(path="error.png") # This helps us see why it failed

        browser.close()

if __name__ == "__main__":
    run_automation()
