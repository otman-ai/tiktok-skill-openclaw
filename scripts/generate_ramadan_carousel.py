import os
import subprocess
import time

# Define the slides
slides = [
    {
        "hook": "6 Things to do in Ramadan 🌙",
        "prompt": "A serene night scene with a crescent moon and lantern, islamic style, ramadan atmosphere, cinematic lighting, photorealistic."
    },
    {
        "hook": "Read Quran daily 📖",
        "prompt": "A person reading the Quran in a mosque, peaceful, serene, islamic architecture, warm lighting."
    },
    {
        "hook": "Give Charity (Zakat) 🤲",
        "prompt": "Hands giving charity or food to someone in need, kindness, compassion, warm colors, soft focus."
    },
    {
        "hook": "Pray Taraweeh 🕌",
        "prompt": "People praying in a beautiful mosque at night, taraweeh prayer, spiritual atmosphere, golden lighting."
    },
    {
        "hook": "Make Dua frequently ✨",
        "prompt": "Hands raised in prayer (dua) under the stars, silhouette, spiritual connection, night sky."
    },
    {
        "hook": "Help others & feed fasting people 🍲",
        "prompt": "A communal iftar meal, people sharing food, happiness, community, ramadan vibes."
    }
]

output_dir = "output/ramadan_carousel"
os.makedirs(output_dir, exist_ok=True)

print(f"Generating {len(slides)} slides for Ramadan carousel...")

for i, slide in enumerate(slides):
    filename = f"slide_{i+1}.png"
    hook = slide["hook"]
    prompt = slide["prompt"]
    
    print(f"Generating Slide {i+1}: '{hook}'...")
    
    cmd = [
        "python3", "skills/tiktok-skill/scripts/generate_image.py",
        "--out-dir", output_dir,
        "--filename", filename,
        "--hook", hook,
        prompt
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"  -> Done: {filename}")
    except subprocess.CalledProcessError as e:
        print(f"  -> Failed to generate slide {i+1}: {e}")

print("All slides generated!")

# Upload and create draft
caption = "Making the most of Ramadan! Here are 6 things you should do this holy month. #ramadan #islam #muslim"
print(f"Uploading to Postiz with caption: '{caption}'...")

upload_cmd = [
    "python3", "skills/tiktok-skill/scripts/upload.py",
    "--caption", caption,
    "--now"  # Post immediately!
]
# Add image paths
import glob
images = sorted(glob.glob(f"{output_dir}/slide_*.png"))
upload_cmd.extend(images)

try:
    subprocess.run(upload_cmd, check=True, env={**os.environ, "PYTHONPATH": f"{os.environ.get('PYTHONPATH', '')}:skills/tiktok-skill"})
    print("Upload successful!")
except subprocess.CalledProcessError as e:
    print(f"Upload failed: {e}")
