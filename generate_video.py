import os
import time
import requests
import random
from playwright.sync_api import sync_playwright

# 1. Get a Prompt (Using fallback if API fails)
def get_ai_prompt():
    themes = [
        "First-person drone POV flying through a massive desert with giant sand dunes at sunset, golden hour, 4k, hyper-realistic, sand particles flying",
        "Cinematic view of a cozy cabin in a dark pine forest during a heavy rainstorm, lightning illuminating the sky, 4k, hyper-detailed textures",
        "Underwater POV swimming through a vibrant coral reef with sun rays piercing the crystal clear water, tropical sea, cinematic lighting",
        "A hyper-realistic 1700s European old town street during a misty morning, cobblestones, lanterns flickering, cinematic atmosphere",
        "A futuristic peaceful mountain temple surrounded by floating cherry blossoms and waterfalls, spiritual and majestic, 8k resolution"
    ]
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    prompt_theme = random.choice(themes)
    
    if not api_key:
        return prompt_theme

    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        data = {
            "model": "meta-llama/llama-3-8b-instruct:free",
            "messages": [{"role": "user", "content": f"Make this prompt eye-catchy: {prompt_theme}"}]
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=10)
        res_json = response.json()
        return res_json['choices'][0]['message']['content']
    except:
        return prompt_theme 

# 2. Automation Logic
def run_automation():
    prompt = get_ai_prompt()
    print(f"🚀 Prompt: {prompt}")

    with sync_playwright() as p:
        # We use a standard browser launch without the 'stealth' library
        browser = p.chromium.launch(headless=True) 
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        # Inject Leonardo Cookie
        cookie_value = os.getenv("LEONARDO_COOKIE")
        if cookie_value:
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

        print("🌐 Opening Leonardo.ai...")
        page.goto("https://app.leonardo.ai/ai-generations", wait_until="domcontentloaded")
        time.sleep(15) 

        try:
            print("✍️ Entering Prompt...")
            # Using a very simple locator
            page.locator("textarea").first.fill(prompt)
            time.sleep(2)
            
            print("🎬 Clicking Generate...")
            page.keyboard.press("Enter")
            
            with open("daily_log.md", "a") as f:
                f.write(f"\n- {time.ctime()}: Triggered for prompt: {prompt}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

        print("✅ Done.")
        browser.close()

if __name__ == "__main__":
    run_automation()
