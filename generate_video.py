import os
import time
import requests
import random
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

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
            {"role": "user", "content": f"Enhance this theme into a mind-blowing, eye-catchy 1-sentence prompt for a 9:16 video: {prompt_theme}"}
        ]
    }
    
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']
    except:
        return prompt_theme # Fallback to manual theme if API fails

# 2. Automation Logic
def run_automation():
    prompt = get_ai_prompt()
    print(f"🚀 Today's Mind-Blowing Prompt: {prompt}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) # Run invisibly in GitHub Actions
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        
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
        stealth_sync(page) # Make it look like a real human

        print("🌐 Opening Leonardo.ai...")
        page.goto("https://app.leonardo.ai/ai-generations", wait_until="networkidle")
        time.sleep(5)

        # Handle 9:16 Aspect Ratio
        try:
            print("📐 Setting Aspect Ratio to 9:16...")
            # This clicks the aspect ratio dropdown/button - paths may change slightly based on UI updates
            page.click("text=9:16") 
        except:
            print("⚠️ Could not find 9:16 button, using default.")

        # Input Prompt
        print("✍️ Entering Prompt...")
        page.fill("textarea", prompt) # Leonardo usually uses a textarea for prompts
        
        # Enable Video/Motion if available
        try:
            page.click("button:has-text('Motion')")
        except:
            pass

        # Generate
        print("🎬 Generating Video...")
        page.keyboard.press("Enter")
        
        # Wait for generation (AI video takes time)
        print("⏳ Waiting 3 minutes for AI to work its magic...")
        time.sleep(180) 

        # Log completion
        with open("daily_log.md", "a") as f:
            f.write(f"\n- **Date:** {time.ctime()} | **Prompt:** {prompt} | Status: Success")

        browser.close()

if __name__ == "__main__":
    run_automation()
