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
        "Cozy cabin in a dark forest, heavy rain hitting windows, lightning flashes, trees swaying, volumetric lighting",
        "Underwater POV, tropical coral reef, fish swimming, sun rays shimmering through blue water, 4k cinematic"
    ]
    api_key = os.getenv("OPENROUTER_API_KEY")
    theme = random.choice(themes)
    try:
        headers = {"Authorization": f"Bearer {api_key}", "HTTP-Referer": "https://github.com/"}
        data = {
            "model": "meta-llama/llama-3-8b-instruct:free",
            "messages": [{"role": "user", "content": f"Create a short 1-sentence prompt for a moving AI video: {theme}"}]
        }
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=15)
        return res.json()['choices'][0]['message']['content']
    except: return theme

def run_automation():
    prompt = get_ai_prompt()
    token = os.getenv("HF_TOKEN")
    video_filename = f"nature_motion_{int(time.time())}.mp4"
    
    print(f"🚀 Prompting for REAL Motion: {prompt}")
    
    # MANUALLY VERIFIED IDS AS OF TODAY
    engines = [
        {"id": "VideoCrafter/VideoCrafter2", "api": "/model_predict"},
        {"id": "ali-vilab/modelscope-text-to-video", "api": "/predict"},
        {"id": "guoyww/AnimateDiff", "api": "/animatediff"}
    ]

    for engine in engines:
        try:
            print(f"🤖 Connecting to {engine['id']}...")
            # We use a longer timeout for the initial handshake
            client = Client(engine['id'], hf_token=token)
            
            print(f"⏳ Generating video (This can take 2-5 minutes)...")
            
            # Universal parameter handling
            if "VideoCrafter" in engine['id']:
                # VideoCrafter2 requires prompt, ddim_steps, and scale
                result = client.predict(
                    prompt, 
                    50, # ddim_steps
                    12, # unconditional_guidance_scale
                    api_name=engine['api']
                )
            else:
                # ModelScope/AnimateDiff standard predict
                result = client.predict(prompt, api_name=engine['api'])
            
            # Extract video path
            video_path = result if isinstance(result, str) else result[0]
            
            shutil.copy(video_path, video_filename)
            print(f"✅ SUCCESS: {video_filename} created via {engine['id']}")
            
            with open("daily_log.md", "a") as f:
                f.write(f"\n- {time.ctime()}: ✅ SUCCESS using {engine['id']}. Generated {video_filename}")
            return True
            
        except Exception as e:
            print(f"⚠️ Engine {engine['id']} failed: {str(e)[:100]}...")
            continue

    print("❌ All Real-Video Engines are currently busy or unreachable.")
    return False

if __name__ == "__main__":
    run_automation()
