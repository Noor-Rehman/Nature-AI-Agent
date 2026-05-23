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
            "messages": [{"role": "user", "content": f"Create a 1-sentence prompt for a moving AI video: {theme}"}]
        }
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=15)
        return res.json()['choices'][0]['message']['content']
    except: return theme

def run_automation():
    prompt = get_ai_prompt()
    token = os.getenv("HF_TOKEN")
    video_filename = f"ai_motion_{int(time.time())}.mp4"
    print(f"🚀 Targeting Motion for: {prompt}")

    # ENGINE A: AnimateDiff-Lightning (The Dream)
    try:
        print("🤖 Trying Engine A (AnimateDiff)...")
        client = Client("ByteDance/AnimateDiff-Lightning", hf_token=token)
        result = client.predict(prompt=prompt, api_name="/generate_video")
        shutil.copy(result, video_filename)
        return True
    except Exception as e:
        print(f"⚠️ Engine A failed: {e}")

    # ENGINE B: ModelScope (The Backup)
    try:
        print("🤖 Trying Engine B (ModelScope)...")
        client = Client("ali-vilab/modelscope-text-to-video", hf_token=token)
        result = client.predict(prompt, api_name="/predict")
        shutil.copy(result, video_filename)
        return True
    except Exception as e:
        print(f"⚠️ Engine B failed: {e}")

    # ENGINE C: FFmpeg AI Animation (The Unstoppable)
    try:
        print("🎨 Engines busy. Switching to FFmpeg AI Animation...")
        for i in range(12): # Generate 12 high-quality AI frames
            print(f"🖼️ Generating AI Frame {i}...")
            seed = random.randint(0, 999999)
            url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=720&height=1280&seed={seed}&model=flux&nologo=true"
            img_data = requests.get(url).content
            with open(f"f_{i:03d}.jpg", 'wb') as f:
                f.write(img_data)
        
        # USE FFMPEG (Built-in tool) to create the video
        # -framerate 6: 6 images per second
        # -pix_fmt yuv420p: Standard format for all phones/YouTube
        print("🎬 FFmpeg is stitching the video...")
        os.system(f"ffmpeg -framerate 6 -i f_%03d.jpg -c:v libx264 -pix_fmt yuv420p {video_filename}")
        
        # Cleanup images
        for i in range(12): os.remove(f"f_{i:03d}.jpg")
        return True
    except Exception as e:
        print(f"❌ All Engines Failed: {e}")
        return False

if __name__ == "__main__":
    success = run_automation()
    with open("daily_log.md", "a") as f:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        f.write(f"\n- {time.ctime()}: {status}")
