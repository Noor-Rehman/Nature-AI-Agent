import os
import time
import requests
import random

# --- LEGACY FIX FOR MOVIEPY ---
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
# ------------------------------

from moviepy.editor import ImageClip

def get_ai_prompt():
    themes = [
        "First-person drone POV flying fast over a cinematic desert with massive sand dunes, golden hour, 8k, hyper-realistic",
        "Immersive first-person view walking through a 1700s European cobblestone town at dawn, misty atmosphere, flickering lanterns",
        "Cinematic 9:16 view of a cozy wooden cabin in a dark pine forest, heavy rain hitting windows, lightning, volumetric lighting",
        "POV swimming through a vibrant tropical coral reef, sun rays piercing blue water, cinematic 4k"
    ]
    api_key = os.getenv("OPENROUTER_API_KEY")
    theme = random.choice(themes)
    try:
        headers = {"Authorization": f"Bearer {api_key}", "HTTP-Referer": "https://github.com/"}
        data = {
            "model": "meta-llama/llama-3-8b-instruct:free",
            "messages": [{"role": "user", "content": f"Enhance this for an eye-catchy 1-sentence 9:16 AI video: {theme}"}]
        }
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=15)
        return res.json()['choices'][0]['message']['content']
    except: return theme

def run_automation():
    prompt = get_ai_prompt()
    print(f"🚀 Mind-Blowing Prompt: {prompt}")
    
    video_filename = f"nature_ai_{int(time.time())}.mp4"
    image_filename = "temp_visual.jpg"

    try:
        # 1. Generate High-End AI Visual (Flux Model)
        print("🎨 Generating AI Visual...")
        encoded_prompt = requests.utils.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&model=flux&nologo=true"
        
        response = requests.get(url, timeout=30)
        with open(image_filename, 'wb') as f:
            f.write(response.content)

        # 2. Transform Image into Cinematic 9:16 Video
        print("🎬 Creating Cinematic Motion Video...")
        # Duration: 5 seconds
        clip = ImageClip(image_filename).set_duration(5)
        
        # Apply a slow zoom-in effect (Drone style)
        # Using a safer scaling method for MoviePy 1.0.3
        clip = clip.resize(lambda t: 1 + 0.03 * t)
        
        # Set video parameters and export
        clip.fps = 24
        clip.write_videofile(video_filename, codec='libx264', audio=False, threads=4)
        
        print(f"✅ Video created: {video_filename}")
        with open("daily_log.md", "a") as f:
            f.write(f"\n- {time.ctime()}: SUCCESS. Created {video_filename}")

    except Exception as e:
        print(f"❌ Error: {e}")
        with open("daily_log.md", "a") as f:
            f.write(f"\n- {time.ctime()}: Error: {str(e)}")

if __name__ == "__main__":
    run_automation()
