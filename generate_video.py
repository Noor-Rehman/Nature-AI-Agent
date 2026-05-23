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
        # We fetch a slightly larger image so we have "room" to zoom in without losing quality
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=1422&model=flux&nologo=true"
        
        response = requests.get(url, timeout=30)
        with open(image_filename, 'wb') as f:
            f.write(response.content)

        # 2. Transform Image into Cinematic 9:16 Video
        print("🎬 Creating Cinematic Motion Video...")
        duration = 5 
        
        # Load clip and force it to be an even size immediately
        clip = ImageClip(image_filename).set_duration(duration)
        
        # PROFESSIONAL ZOOM FIX: 
        # Instead of resizing the frame (which causes the lines), 
        # we resize the original image once and then "pan" or use a stable resize
        base_w, base_h = 720, 1280
        clip = clip.resize(width=base_w) # Ensure width is 720
        
        # Apply zoom by resizing and then cropping to the exact center
        # This keeps the pixel grid perfectly aligned
        def zoom(t):
            return 1 + 0.04 * (t / duration)
            
        # We use a trick: resize then crop to ensure dimensions are always 720x1280
        clip = clip.resize(zoom).on_color(size=(base_w, base_h), color=(0,0,0), pos='center')
        
        print("💾 Final Encoding with Rounding Fix...")
        clip.write_videofile(
            video_filename, 
            fps=24, 
            codec='libx264', 
            audio=False, 
            # This is the "Magic Bullet" parameter that forces the video to stay 720x1280
            ffmpeg_params=['-vf', 'scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2', '-pix_fmt', 'yuv420p']
        )
        
        print(f"✅ Video created successfully: {video_filename}")
        with open("daily_log.md", "a") as f:
            f.write(f"\n- {time.ctime()}: ✅ SUCCESS. Created {video_filename}")

    except Exception as e:
        print(f"❌ Error: {e}")
        with open("daily_log.md", "a") as f:
            f.write(f"\n- {time.ctime()}: ❌ Error: {str(e)}")

if __name__ == "__main__":
    run_automation()
