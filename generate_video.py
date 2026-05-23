import os
import time
import requests
import random
from playwright.sync_api import sync_playwright

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
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/rehman/nature-agent", # Required by some OpenRouter models
    }
    
    data = {
        "model": "meta-llama/llama-3-8b-instruct:free",
        "messages": [
            {"role": "system", "content": "You are a world-class AI Video prompt engineer. Your prompts are vivid and cinematic."},
            {"role": "user", "content": f"Transform this theme into a mind-blowing, eye-catchy 1-sentence prompt for a 9:16 vertical video. Focus on 'volumetric lighting', 'unreal engine 5', and 'hyper-realistic': {prompt_theme}"}
        ]
    }
    
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        res_json = response.json()
        if 'choices' in res_json:
            return res_json['choices'][0]['message']['content']
        else:
            print(f"API Response Error: {res_json}")
            return prompt_theme
    except Exception as e:
        print(f"AI API Error: {e}")
        return prompt_theme 

# 2. Automation Logic
def run_automation():
    prompt = get_ai_prompt()
    print(f"🚀 Today's Mind-Blowing Prompt: {prompt}")

    with sync_playwright() as p:
        # Manual Stealth Configuration
        browser = p.chromium.launch(headless=True) 
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
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

        print("🌐 Opening Leonardo.ai...")
        # Use a more direct URL to the generation tool
        page.goto("https://app.leonardo.ai/ai-generations", wait_until="domcontentloaded")
        time.sleep(15) # Longer wait for Leonardo's heavy UI

        try:
            # Look for the prompt box
            print("✍️ Entering Prompt...")
            # Leonardo's UI often uses a textarea for the prompt
            prompt_box = page.locator("textarea").first
            prompt_box.click()
            prompt_box.fill(prompt)
            time.sleep(2)
            
            # Click the Generate button
            print("🎬 Triggering Generation...")
            # We press Enter as it's the most reliable way to trigger the 'Generate' button
            page.keyboard.press("Enter")
            
            # Success Logging
            log_msg = f"\n- **Date:** {time.ctime()} | **Status:** Triggered | **Prompt:** {prompt}"
            print(log_msg)
            with open("daily_log.md", "a") as f:
                f.write(log_msg)
                
        except Exception as e:
            err_msg = f"❌ Error during generation: {str(e)}"
            print(err_msg)
            with open("daily_log.md", "a") as f:
                f.write(f"\n- **Date:** {time.ctime()} | **Status:** {err_msg}")

        print("✅ Agent finished its task for today.")
        browser.close()

if __name__ == "__main__":
    run_automation()
