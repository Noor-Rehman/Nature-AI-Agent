import os
import time
import requests
import random
import shutil
from gradio_client import Client

def get_ai_prompt():
    themes = [
        "First-person drone POV flying fast through massive desert sand dunes at sunset, sand blowing in the wind, 4k, cinematic motion",
        "Cinematic view of a cozy cabin in a dark forest, heavy rain pouring down, lightning flashing in the sky, trees swaying, hyper-realistic",
        "Underwater POV swimming through a coral reef, fish moving, sun rays shimmering through moving water, 4k cinematic",
        "Walking through a misty 1700s European town, fog rolling in, lanterns flickering, immersive cinematic motion"
    ]
    api_key = os.getenv("OPENROUTER_API_KEY")
    theme = random.choice(themes)
    try:
        headers = {"Authorization": f"Bearer {api_key}", "HTTP-Referer": "https://github.com/"}
        data = {
            "model": "meta-llama/llama-3-8b-instruct:free",
            "messages": [{"role": "user", "content": f"Create a short 1-sentence prompt for a moving AI video. Describe the motion (rain falling, flying, etc) vividly: {theme}"}]
        }
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=15)
        return res.json()['choices'][0]['message']['content']
    except: return theme

def run_automation():
    prompt = get_ai_prompt()
    token = os.getenv("HF_TOKEN")
    video_filename = f"nature_motion_{int(time.time())}.mp4"
    
    print(f"🚀 Prompting for REAL Motion: {prompt}")
    
    # List of High-End Video Engines (Text-to-Video)
    # These are currently the most stable 'Spaces' on Hugging Face
    engines = [
        {"id": "Lightricks/LTX-Video", "api": "/generate_video"},
        {"id": "ByteDance/AnimateDiff-Lightning", "api": "/generate_video"},
        {"id": "damo-vilab/modelscope-text-to-video-ms", "api": "/predict"},
        {"id": "a-r-r-o-w/LTX-Video-UI", "api": "/predict"}
    ]

    for engine in engines:
        try:
            print(f"🤖 Connecting to {engine['id']}...")
            client = Client(engine['id'], hf_token=token)
            
            # The parameters change slightly per model, but most take 'prompt'
            if "LTX-Video" in engine['id']:
                # LTX-Video parameters
                result = client.predict(
                    prompt=prompt,
                    negative_prompt="low quality, blurry, static, distorted",
                    width=480, # Keep resolution low for faster free generation
                    height=848, # Vertical 9:16
                    num_frames=121,
                    steps=20,
                    api_name=engine['api']
                )
            else:
                # Standard Text-to-Video parameters
                result = client.predict(prompt, api_name=engine['api'])
            
            # result is typically a string path to the mp4
            video_path = result if isinstance(result, str) else result[0]
            
            shutil.copy(video_path, video_filename)
            print(f"✅ REAL MOTION VIDEO CREATED via {engine['id']}")
            
            with open("daily_log.md", "a") as f:
                f.write(f"\n- {time.ctime()}: SUCCESS. Created {video_filename} using {engine['id']}")
            return True
            
        except Exception as e:
            print(f"⚠️ Engine {engine['id']} failed: {e}")
            continue

    print("❌ All Real-Video Engines are currently busy or down.")
    return False

if __name__ == "__main__":
    run_automation()
