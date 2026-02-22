import os
import base64
import argparse
from pathlib import Path
import requests
from PIL import Image, ImageDraw, ImageFont
import openai


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    OPENAI_API_KEY = None

client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def generate_image(prompt: str, output_path: str, size: str = "1024x1536") -> str:
    """Generate a single image using the OpenAI Images API and save to output_path.

    Falls back to a simple placeholder image if the API key is not set.
    Supports responses that return a URL or base64-encoded data under 'b64_json'.
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    if client is None:
        # placeholder for local testing
        img = Image.new("RGB", (768, 1152), color=(30, 30, 30))
        draw = ImageDraw.Draw(img)
        draw.text((20, 20), "PLACEHOLDER IMAGE\n" + prompt[:200], fill=(255, 255, 255))
        img.save(out)
        return str(out)

    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size=size,
        n=1,
    )

    image_bytes = None

    # Try many common response shapes: object with .data, dict with data list, b64_json or url
    if hasattr(response, "data") and response.data:
        item = response.data[0]
        # item may be an object with attributes or a dict
        b64 = getattr(item, "b64_json", None) or (item.get("b64_json") if isinstance(item, dict) else None)
        url = getattr(item, "url", None) or (item.get("url") if isinstance(item, dict) else None)
        if b64:
            image_bytes = base64.b64decode(b64)
        elif url:
            image_bytes = requests.get(url).content

    if image_bytes is None and isinstance(response, dict):
        data = response.get("data")
        if data and isinstance(data, list):
            item = data[0]
            if isinstance(item, dict):
                if item.get("b64_json"):
                    image_bytes = base64.b64decode(item["b64_json"])
                elif item.get("url"):
                    image_bytes = requests.get(item["url"]).content

    if image_bytes:
        with open(out, "wb") as f:
            f.write(image_bytes)
        return str(out)

    # fallback placeholder
    img = Image.new("RGB", (768, 1152), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), "PLACEHOLDER (no image returned)" + prompt[:200], fill=(255, 255, 255))
    img.save(out)
    return str(out)


def add_text_overlay(image_path: str, text: str, output_path: str, font_size_percent: float = 0.065) -> str:
    """Add centered wrapped text over an image and save result."""
    img = Image.open(image_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    width, height = img.size

    font_size = int(height * font_size_percent)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
    except Exception:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

    words = text.split()
    lines = []
    cur = []
    for w in words:
        cur.append(w)
        sample = " ".join(cur)
        bbox = draw.textbbox((0, 0), sample, font=font)
        if bbox[2] - bbox[0] > width * 0.8:
            cur.pop()
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))

    y_text = int(height * 0.35)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        line_h = bbox[3] - bbox[1]
        x = (width - line_w) // 2
        draw.text((x, y_text), line, font=font, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
        y_text += line_h + 6

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out)
    return str(out)


def main():
    parser = argparse.ArgumentParser(description="Generate an image with OpenAI gpt-image-1 and optionally overlay a hook text")
    parser.add_argument('prompt', help='Prompt describing the image to generate')
    parser.add_argument('--out-dir', default='images', help='Directory to save the generated image')
    parser.add_argument('--filename', default='image.png', help='Filename for the generated image')
    parser.add_argument('--size', default='1024x1536', help='Image size, e.g. 1024x1536')
    parser.add_argument('--hook', default=None, help='Optional short text to overlay on the image')
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    img_path = out_dir / args.filename

    print(f"Generating image for prompt: {args.prompt[:120]}")
    try:
        saved = generate_image(args.prompt, str(img_path), size=args.size)
        print("Saved image to:", saved)
    except Exception as e:
        print("Image generation failed:", e)
        return

    if args.hook:
        final = out_dir / f"final_{args.filename}"
        try:
            overlayed = add_text_overlay(str(img_path), args.hook, str(final))
            print("Saved overlay image to:", overlayed)
        except Exception as e:
            print("Overlay failed, keeping original image. Error:", e)


if __name__ == '__main__':
    main()
