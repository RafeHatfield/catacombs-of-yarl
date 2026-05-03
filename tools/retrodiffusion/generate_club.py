# generate_club.py

import requests
import base64
import os
import numpy as np

from PIL import Image
from io import BytesIO

API_KEY = os.environ.get("RD_API_KEY", "YOUR_API_KEY_HERE")
ORYX_STYLE = "user__oryx_16_bit_fantasy_style_d970121a"  # Your saved style ID from Step 3

# Load palette as base64
with open("oryx_palette.png", "rb") as f:
    palette_b64 = base64.b64encode(f.read()).decode("utf-8")

url = "https://api.retrodiffusion.ai/v1/inferences"
headers = {"X-RD-Token": API_KEY}

payload = {
    "prompt": "a simple wooden club weapon, thick end on top tapering to thin handle, "
              "dark wood with grain detail, small sprite on transparent background, "
              "accentuate the details so it is clear when reduced in size, top-down RPG item icon",
    "prompt_style": "rd_pro__fantasy",  # or try "rd_pro__fantasy" if no custom style yet ORYX_STYLE
    "width": 64,          # Generate at 2x target size for better detail
    "height": 64,
    "num_images": 1,      # Generate 4 variants, pick the best one
    "input_palette": palette_b64,  # Lock to Oryx colors
    "remove_bg": True,    # Transparent background
}

# payload = {
#     "prompt": "a simple wooden club weapon",
#     "prompt_style": "rd_pro__fantasy",
#     "width": 64,
#     "height": 64,
#     "num_images": 1
# }
# ,        # Just 1 image
#     "check_cost": True,     # Don't generate, just tell me the cost
response = requests.post(url, headers=headers, json=payload)
data = response.json()

print(f"Raw response: {data}")

if "detail" in data:
    print(f"API error: {data['detail']}")
    exit(1)

print(f"Credits used: {data.get('credit_cost') or data.get('credits_used') or data.get('cost', 'unknown')}")
print(f"Credits remaining: {data.get('remaining_credits') or data.get('credits_remaining', 'unknown')}")

print(f"Cost: ${data.get('balance_cost', 'unknown')}")
print(f"Remaining: ${data.get('remaining_balance', 'unknown')}")


for i, img_b64 in enumerate(data["base64_images"]):
    img_bytes = base64.b64decode(img_b64)
    img = Image.open(BytesIO(img_bytes)).convert("RGBA")
    arr = np.array(img)

    # Flood-fill from edges to remove dark background
    h, w = arr.shape[:2]
    visited = np.zeros((h, w), dtype=bool)
    is_bg = np.zeros((h, w), dtype=bool)

    stack = []
    for x in range(w):
        stack.append((x, 0))
        stack.append((x, h-1))
    for y in range(h):
        stack.append((0, y))
        stack.append((w-1, y))

    while stack:
        x, y = stack.pop()
        if x < 0 or x >= w or y < 0 or y >= h or visited[y, x]:
            continue
        visited[y, x] = True
        r, g, b, a = arr[y, x]
        if int(r) + int(g) + int(b) < 30:
            is_bg[y, x] = True
            stack.extend([(x+1,y),(x-1,y),(x,y+1),(x,y-1)])

    arr[is_bg] = [0, 0, 0, 0]
    img = Image.fromarray(arr)

    img.save(f"club_64x64_{i}.png")
    img_16 = img.resize((16, 16), Image.NEAREST)
    img_16.save(f"club_16x16_{i}.png")
    print(f"Saved club variant {i}")