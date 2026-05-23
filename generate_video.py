import os
import time
import requests
import random
import numpy as np
from moviepy.editor import ImageClip, vfx

def get_ai_prompt():
    themes = [
        "First-person drone POV flying fast over a cinematic desert with massive sand dunes, golden hour, sand dust, 8k, hyper-realistic",
        "Immersive first-person view walking through a 1700s European cobblestone town at dawn, misty atmosphere, flickering lanterns, ultra-detailed",
        "Cinematic 9:16 view of a cozy wooden cabin in a dark pine forest, heavy rain hitting windows, lightning illuminating the trees, volumetric lighting",
        "POV swimming through a vibrant tropical coral reef, sun rays piercing crystal clear blue water, cinematic 4k, hyper-detailed sea life"
    ]
    api_key = os.getenv("OPENROUTER_API_KEY")
    theme = random.choice(themes)
    try:
        headers = {"Authorization": f"Bearer {api_key}", "HTTP-Referer": "https://github.com/"}
        data = {
            "model": "meta-llama/llama-3-8b-instruct:free",
            "messages": [{"role": "user", "content": f"Create a mind-blowing, eye-catchy 1-sentence AI prompt for: {theme}. Focus on extreme detail and cinematic lighting."}]
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
        # 1. Generate High-End AI Visual (Flux Model - Best in the world)
        print("🎨 Generating AI Visual...")
        encoded_prompt = requests.utils.quote(prompt)
        # We force 9:16 aspect ratio (1080x1920)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&model=flux&nologo=true"
        
        img_data = requests.get(url).content
        with open(image_filename, 'wb') as handler:
            handler.write(img_data)

        # 2. Transform Image into Cinematic 9:16 Video
        print("🎬 Creating Cinematic Motion Video...")
        duration = 5 # 5 second video
        clip = ImageClip(image_filename).set_duration(duration)
        
        # Add a "Ken Burns" effect (Slow zoom in to look like a drone shot)
        clip = clip.fx(vfx.zoom_in, 0.05, duration) 
        
        clip.write_videofile(video_filename, fps=24, codec='libx264')
        print(f"✅ Video successfully created: {video_filename}")

        with open("daily_log.md", "a") as f:
            f.write(f"\n- {time.ctime()}: SUCCESS. Generated {video_filename}")

    except Exception as e:
        print(f"❌ Error: {e}")
        with open("daily_log.md", "a") as f:
            f.write(f"\n- {time.ctime()}: Error occurred: {str(e)}")

if __name__ == "__main__":
    run_automation()
