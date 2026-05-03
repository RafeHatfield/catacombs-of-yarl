from PIL import Image
img = Image.open("club_64x64_0.png").convert("RGBA")
# Check: does the 64x64 have transparent pixels?
pixels = img.load()
transparent = sum(1 for y in range(64) for x in range(64) if pixels[x, y][3] == 0)
print(f"64x64 transparent pixels: {transparent} / 4096")

# Now resize and check
small = img.resize((16, 16), Image.NEAREST)
small_pixels = small.load()
transparent_small = sum(1 for y in range(16) for x in range(16) if small_pixels[x, y][3] == 0)
print(f"16x16 transparent pixels: {transparent_small} / 256")

small.save("club_16x16_0.png")