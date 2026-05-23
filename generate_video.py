import os
import time
import requests
import random
from playwright.sync_api import sync_playwright

def get_ai_prompt():
    themes = [
        "First-person drone POV flying through a massive desert with giant sand dunes at sunset, golden hour, 8k, unreal engine 5 style",
        "Cinematic view of a cozy cabin in a dark pine forest during a heavy rainstorm, lightning, hyper-realistic, volumetric lighting",
        "Underwater POV swimming through a vibrant coral reef, sun rays piercing the water, 8k resolution, cinematic",
        "A hyper-realistic 1700s European old town street during a misty morning, lanterns flickering, octane render",
        "A futuristic peaceful mountain temple surrounded by floating cherry blossoms and waterfalls, 8k resolution"
    ]
    api_key = os.getenv("OPENROUTER_API_KEY")
    theme = random.choice(themes)
    try:
        headers = {"Authorization": f"Bearer {api_key}", "HTTP-Referer": "https://github.com/"}
        data = {
            "model": "meta-llama/llama-3-8b-instruct:free",
            "messages": [{"role": "user", "content": f"Enhance this for a 9:16 eye-catchy AI video prompt: {theme}"}]
        }
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=15)
        return res.json()['choices'][0]['message']['content']
    except: return theme

def run_automation():
    prompt = get_ai_prompt()
    print(f"🚀 Prompt: {prompt}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a very common screen size
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        
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
            print("🌐 Navigating to Leonardo AI Generations...")
            # We use a longer timeout for the page load
            page.goto("https://app.leonardo.ai/ai-generations", wait_until="domcontentloaded", timeout=100000)
            
            print("⏳ Waiting 40 seconds for heavy UI to load...")
            time.sleep(40) 

            # Take a screenshot to see if we are logged in or stuck at login
            page.screenshot(path="debug_view.png")
            print("📸 Debug screenshot saved as debug_view.png")

            print("✍️ Attempting to fill prompt...")
            # Try to find the prompt box by its most common attribute
            prompt_box = page.locator("textarea").first
            prompt_box.wait_for(state="visible", timeout=60000)
            prompt_box.click()
            page.keyboard.type(prompt, delay=100)
            
            print("🎬 Sending Enter command...")
            page.keyboard.press("Enter")
            time.sleep(10)
            
            with open("daily_log.md", "a") as f:
                f.write(f"\n- {time.ctime()}: ✅ Video triggered for: {prompt}")
            print("✅ Success!")

        except Exception as e:
            print(f"❌ Error: {e}")
            page.screenshot(path="error_state.png")
            with open("daily_log.md", "a") as f:
                f.write(f"\n- {time.ctime()}: ❌ Failed. See error_state.png. Error: {str(e)}")

        browser.close()

if __name__ == "__main__":
    run_automation()
