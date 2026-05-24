import os
import requests
from PIL import Image, ImageDraw
import imageio.v2 as imageio
import numpy as np
import random

# -----------------------------
# Prompt Generator
# -----------------------------
def get_prompt():
    return random.choice([
        "underwater coral reef cinematic lighting, fish swimming",
        "foggy medieval street lanterns glowing at night",
        "rainy forest cabin with lightning storm",
        "desert sunset cinematic drone shot, golden light"
    ])

# -----------------------------
# Generate Base Image
# -----------------------------
def generate_image(prompt):
    print("🎨 Generating base image...")
    url = f"https://image.pollinations.ai/prompt/{prompt}"
    response = requests.get(url, timeout=60)

    with open("base.jpg", "wb") as f:
        f.write(response.content)

    return Image.open("base.jpg").convert("RGB")

# -----------------------------
# Add Particles (scene aware)
# -----------------------------
def add_particles(img, prompt, frame_idx):
    draw = ImageDraw.Draw(img)
    w, h = img.size

    for _ in range(40):
        x = random.randint(0, w)
        y = random.randint(0, h)

        # Scene-based behavior
        if "underwater" in prompt:
            y -= frame_idx * 2  # bubbles go up
        elif "rain" in prompt:
            y += frame_idx * 4  # rain falls fast
        else:
            y += frame_idx * 1  # default drift

        size = random.randint(1, 3)

        if "rain" in prompt:
            draw.line((x, y, x, y+5), fill=(200, 200, 255))
        else:
            draw.ellipse((x, y, x+size, y+size), fill=(255, 255, 255))

    return img

# -----------------------------
# Create Motion Frames
# -----------------------------
def create_motion_frames(image, prompt, frames=20):
    print("🎬 Creating cinematic AI-style motion...")

    images = []
    w, h = image.size

    # Background layer (blur effect)
    background = image.resize((w//2, h//2)).resize((w, h))

    for i in range(frames):
        # Camera motion
        zoom = 1 + (i * 0.01)
        shift_x = int(np.sin(i / 3) * 15)
        shift_y = int(np.cos(i / 4) * 10)

        # Background (slow movement)
        bg = background.copy()
        bg = bg.transform(
            (w, h),
            Image.AFFINE,
            (1, 0, shift_x * 0.3, 0, 1, shift_y * 0.3)
        )

        # Foreground (faster movement)
        fg_w, fg_h = int(w * zoom), int(h * zoom)
        fg = image.resize((fg_w, fg_h))

        left = (fg_w - w)//2 + shift_x
        top = (fg_h - h)//2 + shift_y
        fg = fg.crop((left, top, left + w, top + h))

        # Blend layers (depth effect)
        blended = Image.blend(bg, fg, alpha=0.7)

        # Add particles
        blended = add_particles(blended, prompt, i)

        images.append(np.array(blended))

    return images

# -----------------------------
# Create Video
# -----------------------------
def create_video(frames):
    print("🎥 Building video...")
    imageio.mimsave("output.mp4", frames, fps=12)

# -----------------------------
# Main Pipeline
# -----------------------------
def main():
    prompt = get_prompt()
    print("🚀 Prompt:", prompt)

    img = generate_image(prompt)

    frames = create_motion_frames(img, prompt, frames=20)

    create_video(frames)

    print("✅ Video created: output.mp4")

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    main()
