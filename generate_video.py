import os
import requests
from PIL import Image
import imageio
import numpy as np
import random
import time

def get_prompt():
    return random.choice([
        "underwater coral reef cinematic lighting, fish swimming",
        "foggy medieval street lanterns glowing at night",
        "rainy forest cabin with lightning storm",
        "desert sunset cinematic drone shot, golden light"
    ])

def generate_image(prompt):
    print("🎨 Generating base image...")

    url = f"https://image.pollinations.ai/prompt/{prompt}"
    response = requests.get(url, timeout=60)

    with open("base.jpg", "wb") as f:
        f.write(response.content)

    return Image.open("base.jpg")

def create_motion_frames(image, frames=20):
    print("🎬 Creating motion frames...")

    images = []
    w, h = image.size

    for i in range(frames):
        scale = 1 + (i * 0.015)  # smooth zoom
        new_w, new_h = int(w * scale), int(h * scale)

        img = image.resize((new_w, new_h))
        img = img.crop((0, 0, w, h))

        images.append(np.array(img))

    return images

def create_video(frames):
    print("🎥 Building video...")
    imageio.mimsave("output.mp4", frames, fps=10)

def main():
    prompt = get_prompt()
    print("🚀 Prompt:", prompt)

    img = generate_image(prompt)
    frames = create_motion_frames(img)

    create_video(frames)

    print("✅ Video created: output.mp4")

if __name__ == "__main__":
    main()
