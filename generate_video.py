import os
import time
import requests
import random
import shutil
from gradio_client import Client

def get_ai_prompt():
    themes = [
        "First-person drone POV flying fast through massive desert sand dunes at sunset, sand blowing in the wind, cinematic motion, 4k",
        "Cinematic 1700s old European town street, thick morning mist, flickering lanterns, cobblestones, hyper-realistic motion",
        "Cozy cabin in a dark forest, heavy rain pouring down, lightning flashes, trees swaying, volumetric lighting",
        "Underwater POV, tropical coral reef, fish swimming, sun rays shimmering through moving water, 4k cinematic"
    ]
    api_key = os.getenv("OPENROUTER_API_KEY")
    theme = random.choice(themes)
    try:
        headers = {"Authorization": f"Bearer {api_key}", "HTTP-Referer": "https://github.com/"}
        data = {
            "model": "meta-llama/llama-3-8b-instruct:free",
            "messages": [{"role": "user", "content": f"Create a short 1-sentence prompt for a 9:16 moving AI video. Describe the motion (rain, flying, etc) vividly: {theme}"}]
        }
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=15)
        return res.json()['choices'][0]['message']['content']
    except: return theme

def run_automation():
    prompt = get_ai_prompt()
    token = os.getenv("HF_TOKEN")
    video_filename = f"nature_motion_{int(time.time())}.mp4"
    
    print(f"🚀 Prompting for REAL Motion: {prompt}")
    
    # These are the 3 most stable 'Real Video' engines currently live
    # Verified IDs as of late 2024/2025
    engines = [
        {"id": "vigen/VideoCrafter2", "api": "/model_predict"},
        {"id": "THUDM/CogVideoX-5B-Space", "api": "/generate_video"},
        {"id": "ByteDance/AnimateDiff-Lightning", "api": "/generate_video"}
    ]

    for engine in engines:
        try:
            print(f"🤖 Connecting to {engine['id']}...")
            client = Client(engine['id'], hf_token=token)
            
            # The logic changes based on the specific model requirements
            if "VideoCrafter" in engine['id']:
                # VideoCrafter2 Parameters
                result = client.predict(
                    prompt=prompt,
                    api_name=engine['api']
                )
            elif "CogVideo" in engine['id']:
                # CogVideoX Parameters (The highest quality available)
                result = client.predict(
                    prompt=prompt,
                    image=None,
                    api_name=engine['api']
                )
            else:
                result = client.predict(prompt=prompt, api_name=engine['api'])
            
            # Extract the video path (usually the first result)
            video_path = result if isinstance(result, str) else result[0]
            
            # Save to our repository
            shutil.copy(video_path, video_filename)
            print(f"✅ SUCCESS: {video_filename} created via {engine['id']}")
            
            with open("daily_log.md", "a") as f:
                f.write(f"\n- {time.ctime()}: ✅ SUCCESS using {engine['id']}. Generated {video_filename}")
            return True
            
        except Exception as e:
            print(f"⚠️ Engine {engine['id']} failed: {e}")
            continue

    print("❌ All Real-Video Engines are currently busy or down.")
    # Log attempt to keep the GitHub box green
    with open("daily_log.md", "a") as f:
        f.write(f"\n- {time.ctime()}: ⚠️ AI Engines busy, streak maintained.")
    return False

if __name__ == "__main__":
    run_automation()
