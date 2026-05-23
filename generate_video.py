import os
import time
import requests
import random
from gradio_client import Client

def get_ai_prompt():
    themes = [
        "First-person drone POV flying fast through massive desert sand dunes at sunset, sand blowing in the wind, 4k, cinematic motion",
        "Cinematic view of a cozy cabin in a dark forest, heavy rain pouring down, lightning flashing in the sky, trees swaying, hyper-realistic",
        "Underwater POV swimming through a coral reef, fish moving, sun rays shimmering through moving water, 4k cinematic",
        "Walking through a misty 1700s European town, fog rolling in, lanterns flickering, people shadows moving in the distance"
    ]
    api_key = os.getenv("OPENROUTER_API_KEY")
    theme = random.choice(themes)
    try:
        headers = {"Authorization": f"Bearer {api_key}", "HTTP-Referer": "https://github.com/"}
        data = {
            "model": "meta-llama/llama-3-8b-instruct:free",
            "messages": [{"role": "user", "content": f"Create a short 1-sentence prompt for a 9:16 moving AI video. Describe the motion (rain falling, flying, etc): {theme}"}]
        }
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=15)
        return res.json()['choices'][0]['message']['content']
    except: return theme

def run_automation():
    prompt = get_ai_prompt()
    token = os.getenv("HF_TOKEN")
    print(f"🚀 Prompting for REAL Motion: {prompt}")
    
    video_filename = f"nature_motion_{int(time.time())}.mp4"

    try:
        # We use a professional Text-to-Video space
        print("🤖 Connecting to AI Video Engine (AnimateDiff-Lightning)...")
        # Use your HF_TOKEN to bypass public queues
        client = Client("ByteDance/AnimateDiff-Lightning", hf_token=token)
        
        # Trigger real video generation (actual motion frames)
        result = client.predict(
            prompt=prompt,
            api_name="/generate_video"
        )
        
        # Result is the path to the real .mp4 file
        import shutil
        shutil.copy(result, video_filename)
        
        print(f"✅ REAL MOTION VIDEO CREATED: {video_filename}")
        with open("daily_log.md", "a") as f:
            f.write(f"\n- {time.ctime()}: ✅ SUCCESS. Created real motion video: {video_filename}")

    except Exception as e:
        print(f"❌ Error: {e}")
        with open("daily_log.md", "a") as f:
            f.write(f"\n- {time.ctime()}: ❌ Motion Engine Busy. Error: {str(e)}")

if __name__ == "__main__":
    run_automation()
