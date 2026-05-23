import os
import time
import requests
import random
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth

# 1. Get a Mind-Blowing Prompt from OpenRouter
def get_ai_prompt():
    api_key = os.getenv("OPENROUTER_API_KEY")
    themes = [
        "First-person drone POV flying through a massive desert with giant sand dunes at sunset, golden hour, 4k, hyper-realistic, sand particles flying",
        "Cinematic view of a cozy cabin in a dark pine forest during a heavy rainstorm, lightning illuminating the sky, 4k, hyper-detailed textures",
        "Underwater POV swimming through a vibrant coral reef with sun rays piercing the crystal clear water, tropical sea, cinematic lighting",
        "A hyper-realistic 1700s European old town street during a misty morning, cobblestones, lanterns flickering, cinematic atmosphere",
        "A futuristic peaceful mountain temple surrounded by floating cherry blossoms and waterfalls, spiritual and majestic, 8k resolution"
    ]
    
    prompt_theme = random.choice(themes)
    
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {
        "model": "meta-llama/llama-3-8b-instruct:free",
        "messages": [
            {"role": "system", "content": "You are a world-class AI Video prompt engineer. Your prompts are vivid, cinematic, and use technical photography terms."},
            {"role": "user", "content": f"Transform this theme into a mind-blowing, eye-catchy 1-sentence prompt for a 9:16 vertical video. Use words like 'octane render', 'volumetric lighting', and 'unreal engine 5' to ensure the result is insane: {prompt_theme}"}
        ]
    }
    
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        res_json = response.json()
        return res_json['choices'][0]['message']['content']
    except Exception as e:
        print(f"AI API Error: {e}")
        return prompt_theme 

# 2. Automation Logic
def run_automation():
    prompt = get_ai_prompt()
    print(f"🚀 Today's Mind-Blowing Prompt: {prompt}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) 
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        
        # Inject Leonardo Cookie
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
        # Corrected import usage
        stealth(page) 

        print("🌐 Opening Leonardo.ai...")
        page.goto("https://app.leonardo.ai/ai-generations", wait_until="networkidle")
        time.sleep(10) 

        # Input Prompt
        try:
            print("✍️ Entering Prompt...")
            # Using a more generic selector to find the prompt textarea
            page.locator("textarea").first.fill(prompt)
            time.sleep(2)
            
            # Click Generate
            print("🎬 Clicking Generate...")
            page.keyboard.press("Enter")
            
            # Log success
            with open("daily_log.md", "a") as f:
                f.write(f"\n- **Date:** {time.ctime()} | **Status:** Triggered | **Prompt:** {prompt}")
                
        except Exception as e:
            print(f"❌ Error during generation: {e}")
            with open("daily_log.md", "a") as f:
                f.write(f"\n- **Date:** {time.ctime()} | **Status:** Error: {str(e)}")

        print("✅ Script finished.")
        browser.close()

if __name__ == "__main__":
    run_automation()
