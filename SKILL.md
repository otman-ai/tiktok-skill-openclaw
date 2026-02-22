# TikTok Carousel Generation Skill (openclaw-style)

Short description
-----------------
This skill generates a 6-slide TikTok carousel (portrait images + text overlays), drafts a TikTok post using a draft API (Postiz in this repository), and outputs a ready-to-review caption. The focus is cost-effective, reproducible content generation and automating as much of the drafting process as possible while keeping final publishing manual.

Quick install & run
-------------------
1. Create and activate a Python virtual environment.
2. Install dependencies: `pip install -r requirements.txt`.
3. Create environment variables: `OPENAI_API_KEY` (for image/text generation) and `POSTIZ_API_KEY` (optional, for uploading and creating drafts).
4. Run the generator (examples in `README.md` / `scripts/`).

What this skill contains
-----------------------
- `tiktok_content_gen.py` — orchestrator: creates hook, locked architecture, images, captions and can upload a draft.
- `postiz_api_integration.py` — small Postiz client used to upload media and create drafts (keeps drafts private by default).
- `scripts/upload.py` — CLI wrapper to upload generated images and create a draft.
- `requirements.txt` — Python dependencies.
- `scripts/generate_image.py` - CLI that generate image and added text overlay if available : usage: scripts/generate_image.py [-h] [--out-dir OUT_DIR] [--filename FILENAME] [--size SIZE] [--hook HOOK] prompt

The output is image generated and saved to the out dir
--------------------------

Security & cost notes
---------------------
- Keep API keys out of source control and use environment variables.
- Image generation costs depend on the model (DALL·E 3 or similar). Use batching or lower-res variants for cost savings.

Installation details and examples are in `README.md` inside this folder.