"""Thin PixelLab API wrapper that bypasses a response-schema bug in pixellab==1.0.5:
the installed SDK's Usage model hardcodes `type: Literal["usd"]`, but this account's
subscription billing now returns `{"type": "generations", "generations": N}`, which
raises a pydantic ValidationError before the image can be read out of the response.
Reuses the SDK's Client for auth/base_url; does the HTTP call and response parsing
directly instead of going through the SDK's broken response model.
"""
import base64
import os
from io import BytesIO

import pixellab
import requests
from PIL import Image


def _client():
    return pixellab.Client(secret=os.environ["PIXELLAB_API_TOKEN"])


def _decode(resp_json):
    img_b64 = resp_json["image"]["base64"]
    return Image.open(BytesIO(base64.b64decode(img_b64))).convert("RGBA")


def generate_image_bitforge(description, image_size, seed=0, no_background=True, **kwargs):
    client = _client()
    request_data = {
        "description": description,
        "image_size": image_size,
        "negative_description": kwargs.pop("negative_description", ""),
        "text_guidance_scale": kwargs.pop("text_guidance_scale", 3.0),
        "extra_guidance_scale": kwargs.pop("extra_guidance_scale", 3.0),
        "style_strength": kwargs.pop("style_strength", 0.0),
        "no_background": no_background,
        "seed": seed,
        **kwargs,
    }
    r = requests.post(f"{client.base_url}/generate-image-bitforge",
                       headers=client.headers(), json=request_data)
    r.raise_for_status()
    return _decode(r.json())


def inpaint(description, image_size, inpainting_image, mask_image, seed=0, no_background=True, **kwargs):
    client = _client()
    request_data = {
        "description": description,
        "image_size": image_size,
        "inpainting_image": pixellab.models.Base64Image.from_pil_image(inpainting_image).model_dump(),
        "mask_image": pixellab.models.Base64Image.from_pil_image(mask_image).model_dump(),
        "negative_description": kwargs.pop("negative_description", ""),
        "text_guidance_scale": kwargs.pop("text_guidance_scale", 3.0),
        "extra_guidance_scale": kwargs.pop("extra_guidance_scale", 3.0),
        "no_background": no_background,
        "seed": seed,
        **kwargs,
    }
    r = requests.post(f"{client.base_url}/inpaint",
                       headers=client.headers(), json=request_data)
    r.raise_for_status()
    return _decode(r.json())


def get_balance():
    client = _client()
    r = requests.get(f"{client.base_url}/balance", headers=client.headers())
    r.raise_for_status()
    return r.json()
