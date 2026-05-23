import os
import time
import requests
import random
from gradio_client import Client

def get_ai_prompt():
    themes = [
        "Cinematic drone shot of a heavy thunderstorm over a tropical island, lightning striking the ocean, 4k",
        "A magical 1700s old town street with glowing lanterns and thick morning mist, hyper-realistic",
        "First-person view flying through a glowing crystal cave with underground waterfalls, 8k",
        "Ethereal forest with floating cherry blossoms and giant glowing mushrooms at night, cinematic"
    ]
    api_key = os.getenv("OPENROUTER_API_KEY")
    theme = random.choice(themes)
    try:
        headers = {"Authorization": f"Bearer {api_key}", "HTTP-Referer": "https://github.com/"}
        data = {
            "model": "meta-llama/llama-3-8b-instruct:free",
            "messages": [{"role": "user", "content": f"Create a 1-sentence mind-blowing AI video prompt for: {theme}. Use 9:16 aspect ratio keywords."}]
        }
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=15)
        return res.json()['choices'][0]['message']['content']
    except: return theme

def run_automation():
    prompt = get_ai_prompt()
    print(f"🚀 AI Prompt: {prompt}")

    try:
        # We connect to a public AI Video space on Hugging Face
        # These are free and meant for programmatic access
        print("🤖 Connecting to AI Video Engine...")
        client = Client("guoyww/AnimateDiff")
        
        # This triggers the actual AI video generation
        result = client.predict(
            prompt=prompt,
            n_prompt="bad quality, blurry, distorted, low resolution",
            motion_module="mm_sd_v15_v2.ckpt",
            step=25,
            guidance_scale=7.5,
            api_name="/generate_video"
        )
        
        # Result is the path to the video
        video_path = result
        new_filename = f"nature_ai_{int(time.time())}.mp4"
        
        # Move the video to our repo
        os.rename(video_path, new_filename)
        print(f"✅ Video Generated and Saved: {new_filename}")

        with open("daily_log.md", "a") as f:
            f.write(f"\n- {time.ctime()}: ✅ SUCCESS. Created {new_filename}")

    except Exception as e:
        print(f"❌ Error: {e}")
        # Fallback to a 'Green Square' log even if AI server is busy
        with open("daily_log.md", "a") as f:
            f.write(f"\n- {time.ctime()}: ⚠️ AI Server Busy. Logged to keep streak alive.")

if __name__ == "__main__":
    run_automation()
