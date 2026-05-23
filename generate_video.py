import os
import time
import requests
import random
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_page

# 1. Get a Mind-Blowing Prompt from OpenRouter
def get_ai_prompt():
    api_key = os.getenv("OPENROUTER_API_KEY")
    themes = [
        "First-person drone POV flying through a massive desert with giant sand dunes at sunset, golden hour, 4k, hyper-realistic",
        "Cinematic view of a cozy cabin in a dark pine forest during a heavy rainstorm, lightning illuminating the sky, 4k",
        "Underwater POV swimming through a vibrant coral reef with sun rays piercing the crystal clear water, tropical sea, ultra-detailed",
        "A hyper-realistic 1700s European old town street during a misty morning, cobblestones, lanterns flickering, immersive",
        "A futuristic peaceful mountain temple surrounded by floating cherry blossoms and waterfalls, spiritual and majestic"
    ]
    
    prompt_theme = random.choice(themes)
    
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {
        "model": "meta-llama/llama-3-8b-instruct:free",
        "messages": [
            {"role": "system", "content": "You are a world-class AI Video prompt engineer. Create a short, high-impact, visual prompt for AI video generation."},
            {"role": "user", "content": f"Enhance this theme into a mind-blowing, eye-catchy 1-sentence prompt for a 9:16 vertical video: {prompt_theme}"}
        ]
    }
    
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"AI API Error: {e}")
        return prompt_theme 

# 2. Automation Logic
def run_automation():
    prompt = get_ai_prompt()
    print(f"🚀 Today's Mind-Blowing Prompt: {prompt}")

    with sync_playwright() as p:
        # Launch browser with a specific User Agent to look more human
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
        stealth_page(page) # CORRECTED FUNCTION NAME

        print("🌐 Opening Leonardo.ai...")
        page.goto("https://app.leonardo.ai/ai-generations", wait_until="networkidle")
        time.sleep(10) # Give it extra time to load

        # Input Prompt
        try:
            print("✍️ Entering Prompt...")
            # Try to find the prompt box - Leonardo's UI can be tricky
            page.get_by_placeholder("Type a prompt...").fill(prompt)
            time.sleep(2)
            
            # Click Generate (pressing Enter is safer)
            print("🎬 Clicking Generate...")
            page.keyboard.press("Enter")
            
            # Success Logging
            with open("daily_log.md", "a") as f:
                f.write(f"\n- **Date:** {time.ctime()} | **Status:** Triggered Generation | **Prompt:** {prompt}")
                
        except Exception as e:
            print(f"❌ Error during generation: {e}")
            with open("daily_log.md", "a") as f:
                f.write(f"\n- **Date:** {time.ctime()} | **Status:** Error: {str(e)}")

        print("✅ Script finished.")
        browser.close()

if __name__ == "__main__":
    run_automation()
