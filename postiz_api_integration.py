import os
import requests
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Credentials from environment variables
POSTIZ_API_KEY = os.getenv("POSTIZ_API_KEY")
POSTIZ_API_URL = os.getenv("POSTIZ_API_URL", "https://api.postiz.com/public/v1")


class PostizError(Exception):
    pass


def _auth_headers() -> Dict[str, str]:
    if not POSTIZ_API_KEY:
        raise PostizError("POSTIZ_API_KEY is not set in environment")
    # Postiz API expects the key directly, without 'Bearer' prefix
    return {"Authorization": f"{POSTIZ_API_KEY}"}


def upload_media_to_postiz(file_path: str) -> Dict[str, Any]:
    """Uploads a local image file to Postiz and returns the parsed JSON response.

    Returns a dict with at least an `id` or `url` depending on API.
    """
    p = Path(file_path)
    if not p.exists():
        raise PostizError(f"file not found: {file_path}")

    url = f"{POSTIZ_API_URL}/upload"
    headers = _auth_headers()
    with p.open('rb') as fh:
        # Send filename and content type to ensure correct extension handling
        files = {'file': (p.name, fh, 'image/png')}
        resp = requests.post(url, headers=headers, files=files)
    try:
        resp.raise_for_status()
    except Exception as e:
        raise PostizError(f"upload failed: {e} - {resp.text}")
    return resp.json()


def create_tiktok_draft(media_objects: List[Dict[str, str]], caption: str, privacy_level: str = "SELF_ONLY", schedule_now: bool = False, integration_id: str = "cmly0kvge01pyru0ywhiscjsx") -> Dict[str, Any]:
    url = f"{POSTIZ_API_URL}/posts"
    headers = _auth_headers()
    headers.update({"Content-Type": "application/json"})
    
    # Schedule time (tomorrow for draft, now for immediate)
    if schedule_now:
        post_time = datetime.datetime.utcnow().isoformat() + "Z"
        post_type = "now"
    else:
        post_time = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).isoformat() + "Z"
        post_type = "schedule"
    
    payload = {
        "type": post_type,
        "date": post_time,
        "shortLink": False,
        "tags": [],
        "posts": [
            {
                "integration": { "id": integration_id },
                "value": [
                    {
                        "content": caption,
                        "image": media_objects
                    }
                ],
                "settings": {
                    "__type": "tiktok",
                    "privacy_level": privacy_level,
                    "duet": False,
                    "stitch": False,
                    "comment": True,
                    "autoAddMusic": "no",
                    "brand_content_toggle": False,
                    "brand_organic_toggle": False,
                    "content_posting_method": "DIRECT_POST"
                }
            }
        ]
    }
    
    resp = requests.post(url, headers=headers, json=payload)
    try:
        resp.raise_for_status()
    except Exception as e:
        raise PostizError(f"create_draft failed: {e} - {resp.text}")
    return resp.json()


def upload_images_and_create_draft(image_paths: List[str], caption: str, schedule_now: bool = False) -> Dict[str, Any]:
    """Convenience: upload list of local images and create a draft. Returns draft response."""
    media_objects = []
    for p in image_paths:
        r = upload_media_to_postiz(p)
        
        # Handle response structure
        # If result is nested in 'result', handle that.
        if 'result' in r:
            r = r['result']
            
        mid = r.get('id')
        mpath = r.get('path')
        
        if mid and mpath:
            media_objects.append({"id": mid, "path": mpath})
        else:
            print(f"Warning: upload response missing id or path: {r}")
            # If we can't get path, we can't use it.
            
    return create_tiktok_draft(media_objects, caption, schedule_now=schedule_now)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Upload images to Postiz and create a TikTok draft')
    parser.add_argument('images', nargs='+')
    parser.add_argument('--caption', default='')
    parser.add_argument('--now', action='store_true', help='Post immediately')
    args = parser.parse_args()
    print(upload_images_and_create_draft(args.images, args.caption, schedule_now=args.now))
