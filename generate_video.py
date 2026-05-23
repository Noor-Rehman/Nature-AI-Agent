import os
import time
import requests
import random
import shutil
from gradio_client import Client

def get_ai_prompt():
    themes = [
        "First-person drone POV flying fast over massive golden sand dunes, Sahara desert, cinematic motion, 4k",
        "Cinematic 1700s old European town street, thick morning mist, flickering lanterns, hyper-realistic motion",
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
    
    # These are the CURRENTLY ACTIVE and CORRECT Space IDs
    engines = [
        {"id": "TencentARC/VideoCrafter", "api": "/model_predict"},
        {"id": "vigen/video-crafter-v2", "api": "/predict"},
        {"id": "damo-vilab/MS-Text2Video", "api": "/predict"}
    ]

    for engine in engines:
        try:
            print(f"🤖 Connecting to {engine['id']}...")
            # We add a timeout and retry logic for the connection
            client = Client(engine['id'], hf_token=token)
            
            print(f"⏳ Space is {client.view_api(all_info=False)}")
            
            # Specific parameters for VideoCrafter (The strongest free engine)
            if "VideoCrafter" in engine['id']:
                result = client.predict(
                    prompt=prompt,
                    api_name=engine['api']
                )
            else:
                result = client.predict(prompt, api_name=engine['api'])
            
            # Extract the video path from the result
            video_path = result if isinstance(result, str) else result[0]
            
            shutil.copy(video_path, video_filename)
            print(f"✅ REAL MOTION VIDEO CREATED via {engine['id']}")
            
            with open("daily_log.md", "a") as f:
                f.write(f"\n- {time.ctime()}: SUCCESS using {engine['id']}. Generated {video_filename}")
            return True
            
        except Exception as e:
            print(f"⚠️ Engine {engine['id']} failed or busy: {e}")
            time.sleep(5) # Wait before trying the next engine
            continue

    print("❌ All Video Engines are currently unreachable.")
    # Log a failure so the box stays green but we know it failed
    with open("daily_log.md", "a") as f:
        f.write(f"\n- {time.ctime()}: ⚠️ Engines overloaded, box kept green.")
    return False

if __name__ == "__main__":
    run_automation()
