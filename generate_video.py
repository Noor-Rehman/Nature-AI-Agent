import os
import random
import torch
from diffusers import AnimateDiffPipeline, MotionAdapter, EulerDiscreteScheduler
from diffusers.utils import export_to_video

def get_prompt():
    themes = [
        "cinematic underwater coral reef, fish swimming, sun rays, ultra realistic, 4k motion",
        "drone flying over desert dunes at sunset, cinematic camera movement",
        "foggy medieval street with lantern lights, slow cinematic motion",
        "rainy forest cabin, lightning flashes, dramatic lighting, ultra realistic"
    ]
    return random.choice(themes)

def main():
    prompt = get_prompt()
    print("🚀 Prompt:", prompt)

    model_id = "guoyww/animatediff-motion-adapter-v1-5-2"

    # Load motion adapter
    adapter = MotionAdapter.from_pretrained(model_id, torch_dtype=torch.float32)

    # Base SD model
    pipe = AnimateDiffPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        motion_adapter=adapter,
        torch_dtype=torch.float32
    )

    pipe.scheduler = EulerDiscreteScheduler.from_config(pipe.scheduler.config)

    # CPU-friendly mode (GitHub Actions compatible)
    pipe.enable_model_cpu_offload()

    print("🎬 Generating video... (this may take a few minutes)")

    result = pipe(
        prompt=prompt,
        num_frames=16,
        guidance_scale=7.5,
        num_inference_steps=25
    )

    output_file = "output.mp4"
    export_to_video(result.frames[0], output_file)

    print(f"✅ Video saved: {output_file}")

if __name__ == "__main__":
    main()
