import os
import time
import requests
import random
import shutil
from gradio_client import Client

def get_ai_prompt():
    themes = [
        "Cinematic drone POV, majestic sand dunes in the Sahara, golden hour light, 4k, hyper-realistic",
        "A peaceful 1700s European village street, morning mist, cobblestones, lanterns flickering, 4k",
        "Cozy mountain cabin, heavy rain on windows, lightning in the dark forest, volumetric lighting",
        "Underwater POV, tropical coral reef, sun rays through crystal clear blue water, cinematic"
    ]
    api_key = os.getenv("OPENROUTER_API_KEY")
    theme = random.choice(themes)
    try:
        headers = {"Authorization": f"Bearer {api_key}", "HTTP-Referer": "https://github.com/"}
        data = {
            "model": "meta-llama/llama-3-8b-instruct:free",
            "messages": [{"role": "user", "content": f"Enhance this for an eye-catchy 9:16 AI video: {theme}"}]
        }
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=15)
        return res.json()['choices'][0]['message']['content']
    except: return theme

def run_automation():
    prompt = get_ai_prompt()
    print(f"🚀 AI Video Prompt: {prompt}")
    
    # Try multiple AI Engines in case one is down
    engines = [
        "ByteDance/AnimateDiff-Lightning", 
        "fffiloni/AnimateDiff-Video-Preview",
        "camenduru/AnimateDiff"
    ]
    
    video_generated = False

    for engine in engines:
        try:
            print(f"🤖 Connecting to {engine}...")
            client = Client(engine)
            
            # AnimateDiff-Lightning usually takes these parameters
            result = client.predict(
                prompt=prompt,
                api_name="/generate_video" 
            )
            
            # The result is usually the path to the mp4
            video_path = result
            new_filename = f"nature_video_{int(time.time())}.mp4"
            shutil.copy(video_path, new_filename)
            
            print(f"✅ Video created: {new_filename}")
            with open("daily_log.md", "a") as f:
                f.write(f"\n- {time.ctime()}: SUCCESS using {engine}. Generated {new_filename}")
            
            video_generated = True
            break # Exit loop if success
            
        except Exception as e:
            print(f"⚠️ Engine {engine} failed: {e}")
            continue

    if not video_generated:
        print("❌ All AI engines were busy or down.")
        with open("daily_log.md", "a") as f:
            f.write(f"\n- {time.ctime()}: AI Engines busy, logged attempt for streak.")

if __name__ == "__main__":
    run_automation()
