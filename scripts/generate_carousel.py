import os
import sys
import json
import argparse
import subprocess
import glob

def main():
    parser = argparse.ArgumentParser(description='Generate and upload a dynamic TikTok carousel')
    parser.add_argument('--slides', required=True, help='Path to JSON file containing slides (list of {"hook": "...", "prompt": "..."})')
    parser.add_argument('--caption', required=True, help='Caption for the TikTok post')
    parser.add_argument('--output-dir', default='output/carousel', help='Output directory for generated images')
    parser.add_argument('--now', action='store_true', help='Post immediately to TikTok')
    
    args = parser.parse_args()

    # Load slides
    try:
        with open(args.slides, 'r') as f:
            slides = json.load(f)
    except Exception as e:
        print(f"Error loading slides file: {e}")
        sys.exit(1)
        
    if not isinstance(slides, list):
        print("Error: Slides file must contain a JSON list of objects.")
        sys.exit(1)

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Generating {len(slides)} slides for carousel...")

    generated_images = []

    for i, slide in enumerate(slides):
        filename = f"slide_{i+1}.png"
        hook = slide.get("hook", "")
        prompt = slide.get("prompt", "")
        
        if not prompt:
            print(f"Skipping slide {i+1}: Missing prompt.")
            continue
            
        print(f"Generating Slide {i+1}: '{hook}'...")
        
        cmd = [
            "python3", "skills/tiktok-skill/scripts/generate_image.py",
            "--out-dir", args.output_dir,
            "--filename", filename,
            "--hook", hook,
            prompt
        ]
        
        try:
            subprocess.run(cmd, check=True)
            generated_images.append(os.path.join(args.output_dir, f"final_{filename}")) # generate_image.py prefixes with final_
            print(f"  -> Done: {filename}")
        except subprocess.CalledProcessError as e:
            print(f"  -> Failed to generate slide {i+1}: {e}")

    if not generated_images:
        print("No images generated. Exiting.")
        sys.exit(1)

    print("All slides generated!")

    # Upload and create draft/post
    print(f"Uploading to Postiz with caption: '{args.caption}'...")

    upload_cmd = [
        "python3", "skills/tiktok-skill/scripts/upload.py",
        "--caption", args.caption
    ]
    
    if args.now:
        upload_cmd.append("--now")
        
    # The upload script expects image paths as arguments.
    # Note: generate_image.py saves the final image as `final_slide_X.png` (with overlay) 
    # and `slide_X.png` (without overlay). We want the final ones.
    # Let's verify the filenames. generate_image.py saves `final_{filename}`.
    
    # We constructed the list `generated_images` above with the expected paths.
    # But let's use glob to be safe if files exist.
    
    # Actually, let's just pass the list we built.
    upload_cmd.extend(generated_images)

    try:
        # Ensure PYTHONPATH includes the skill directory so imports work
        env = os.environ.copy()
        pythonpath = env.get("PYTHONPATH", "")
        skill_dir = os.path.abspath("skills/tiktok-skill")
        env["PYTHONPATH"] = f"{pythonpath}:{skill_dir}" if pythonpath else skill_dir
        
        subprocess.run(upload_cmd, check=True, env=env)
        print("Upload successful!")
    except subprocess.CalledProcessError as e:
        print(f"Upload failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
