import os
import time
import requests
import random
import shutil
from gradio_client import Client
import PIL.Image

# Legacy Fix
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
from moviepy.editor import ImageSequenceClip

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

    # ENGINE A: AnimateDiff-Lightning
    try:
        print("🤖 Trying Engine A (AnimateDiff)...")
        client = Client("ByteDance/AnimateDiff-Lightning", hf_token=token)
        result = client.predict(prompt=prompt, api_name="/generate_video")
        shutil.copy(result, video_filename)
        print("✅ Success with Engine A")
        return True
    except Exception as e:
        print(f"⚠️ Engine A failed: {e}")

    # ENGINE B: ModelScope Fallback
    try:
        print("🤖 Trying Engine B (ModelScope)...")
        client = Client("ali-vilab/modelscope-text-to-video", hf_token=token)
        result = client.predict(prompt, api_name="/predict")
        shutil.copy(result, video_filename)
        print("✅ Success with Engine B")
        return True
    except Exception as e:
        print(f"⚠️ Engine B failed: {e}")

    # ENGINE C: The "Unstoppable" Stop-Motion Animation (Pollinations)
    try:
        print("🎨 Engines busy. Switching to Engine C (AI Stop-Motion Animation)...")
        frames = []
        for i in range(12): # Generate 12 unique AI frames
            print(f"🖼️ Generating AI Frame {i+1}/12...")
            # We add a slight seed change to each frame to create "AI jitter" motion
            seed = random.randint(0, 999999)
            url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=720&height=1280&seed={seed}&model=flux&nologo=true"
            img_data = requests.get(url).content
            frame_path = f"frame_{i}.jpg"
            with open(frame_path, 'wb') as f:
                f.write(img_data)
            frames.append(frame_path)
            time.sleep(1) # Don't overwhelm the API
        
        # Stitch frames into a 6fps video (looks like a trippy AI time-lapse)
        clip = ImageSequenceClip(frames, fps=6)
        clip.write_videofile(video_filename, codec='libx264')
        print(f"✅ Success with Engine C (AI Animation)")
        
        # Cleanup frames
        for f in frames: os.remove(f)
        return True
    except Exception as e:
        print(f"❌ All Engines Failed: {e}")
        return False

if __name__ == "__main__":
    success = run_automation()
    if success:
        with open("daily_log.md", "a") as f:
            f.write(f"\n- {time.ctime()}: ✅ SUCCESS. Video generated.")
    else:
        with open("daily_log.md", "a") as f:
            f.write(f"\n- {time.ctime()}: ❌ All AI Engines down.")
