# clean_existing.py
import numpy as np
from PIL import Image

img = Image.open("club_64x64_0.png").convert("RGBA")
arr = np.array(img)
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
img.save("club_64x64_0.png")
img.resize((16, 16), Image.NEAREST).save("club_16x16_0.png")
print("Cleaned!")