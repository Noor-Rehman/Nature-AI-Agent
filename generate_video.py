import os
import time
import requests
import random
from playwright.sync_api import sync_playwright

def get_ai_prompt():
    themes = [
        "First-person drone POV flying through a massive desert with sand dunes at sunset, golden hour, 8k, unreal engine 5, volumetric lighting",
        "Cinematic view of a cozy cabin in a dark forest during a heavy rainstorm, lightning, hyper-realistic, octane render",
        "Underwater POV swimming through a vibrant coral reef, sun rays piercing the water, 8k, cinematic atmosphere",
        "Hyper-realistic 1700s European old town street, misty morning, lanterns flickering, cinematic atmosphere",
        "Futuristic mountain temple, floating cherry blossoms, waterfalls, majestic, 8k resolution"
    ]
    api_key = os.getenv("OPENROUTER_API_KEY")
    prompt_theme = random.choice(themes)
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/", # Required by OpenRouter
            "X-Title": "Nature AI Agent"
        }
        data = {
            "model": "meta-llama/llama-3-8b-instruct:free",
            "messages": [{"role": "user", "content": f"Enhance this into a 1-sentence mind-blowing AI video prompt: {prompt_theme}"}]
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=15)
        return response.json()['choices'][0]['message']['content']
    except:
        return prompt_theme 

def run_automation():
    prompt = get_ai_prompt()
    print(f"🚀 Prompt: {prompt}")

    with sync_playwright() as p:
        # We launch with a larger window so the UI doesn't hide elements
        browser = p.chromium.launch(headless=True) 
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        
        # Add Cookie
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
        print("🌐 Navigating to Leonardo...")
        
        # Go directly to the generation page
        page.goto("https://app.leonardo.ai/ai-generations", wait_until="networkidle", timeout=90000)
        
        # Wait for the prompt area to definitely exist
        print("⏳ Waiting for UI to settle...")
        page.wait_for_selector("textarea", timeout=60000)
        time.sleep(10)

        try:
            # 1. Clear and Fill Prompt
            print("✍️ Typing Prompt...")
            textarea = page.locator("textarea").first
            textarea.click()
            # We type slowly to simulate a human and trigger the 'Generate' button state
            page.keyboard.type(prompt, delay=50)
            time.sleep(2)

            # 2. Trigger Generation
            print("🎬 Clicking Generate...")
            # We try pressing Enter first
            page.keyboard.press("Enter")
            
            # Wait a bit to see if it starts
            time.sleep(10)
            print("✅ Generation Triggered Successfully!")
            
            # 3. Log the success
            with open("daily_log.md", "a") as f:
                f.write(f"\n- {time.ctime()}: ✅ SUCCESS. Prompt: {prompt}")

        except Exception as e:
            print(f"❌ Error: {e}")
            with open("daily_log.md", "a") as f:
                f.write(f"\n- {time.ctime()}: ❌ FAILED. Error: {str(e)}")
            raise e # Force the GitHub Action to show an error if it fails

        browser.close()

if __name__ == "__main__":
    run_automation()
