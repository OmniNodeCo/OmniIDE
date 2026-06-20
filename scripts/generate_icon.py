"""
Generate application icons for all platforms.
Run once to create assets/icon.ico and assets/icon.png.

Usage:
    pip install pillow
    python scripts/generate_icon.py
"""

import os
import sys

# Ensure we can import from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image, ImageDraw


def generate_icons():
    os.makedirs("assets", exist_ok=True)

    sizes = [16, 32, 48, 64, 128, 256, 512]
    images = []

    for size in sizes:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Outer circle — dark background
        margin = size // 8
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=(30, 30, 46, 255),
        )

        # Accent ring — blue
        ring_w = max(2, size // 16)
        ring_m = size // 5
        draw.ellipse(
            [ring_m, ring_m, size - ring_m, size - ring_m],
            outline=(137, 180, 250, 255),
            width=ring_w,
        )

        # Inner circle — purple ring
        inner = size // 4
        inner_w = max(1, size // 20)
        draw.ellipse(
            [inner, inner, size - inner, size - inner],
            outline=(203, 166, 247, 200),
            width=inner_w,
        )

        # Center dot — pink
        center = size // 2
        dot = max(2, size // 10)
        draw.ellipse(
            [center - dot, center - dot, center + dot, center + dot],
            fill=(245, 194, 231, 255),
        )

        # Bracket hints (only on larger sizes)
        if size >= 48:
            bracket_size = size // 8
            bracket_y = center
            bracket_x_left = center - size // 5
            bracket_x_right = center + size // 5

            # < bracket
            for dy in range(-bracket_size, bracket_size + 1):
                dx = abs(dy) * bracket_size // bracket_size
                px = bracket_x_left + dx
                py = bracket_y + dy
                if 0 <= px < size and 0 <= py < size:
                    try:
                        draw.point((px, py), fill=(203, 166, 247, 255))
                        if size >= 128:
                            draw.point((px + 1, py), fill=(203, 166, 247, 255))
                    except Exception:
                        pass

            # > bracket
            for dy in range(-bracket_size, bracket_size + 1):
                dx = -abs(dy) * bracket_size // bracket_size
                px = bracket_x_right + dx
                py = bracket_y + dy
                if 0 <= px < size and 0 <= py < size:
                    try:
                        draw.point((px, py), fill=(137, 180, 250, 255))
                        if size >= 128:
                            draw.point((px - 1, py), fill=(137, 180, 250, 255))
                    except Exception:
                        pass

        images.append(img)

    # Save .ico (Windows) — max 256x256
    ico_images = [img for img in images if img.size[0] <= 256]
    ico_images[0].save(
        "assets/icon.ico",
        format="ICO",
        sizes=[(img.size[0], img.size[1]) for img in ico_images],
        append_images=ico_images[1:],
    )

    # Save .png (general use) — 256x256
    for img in images:
        if img.size[0] == 256:
            img.save("assets/icon.png", format="PNG")
            break

    # Save large .png (512x512) for macOS
    images[-1].save("assets/icon-512.png", format="PNG")

    print("Generated:")
    print("  assets/icon.ico     (Windows)")
    print("  assets/icon.png     (256x256)")
    print("  assets/icon-512.png (512x512)")
    print()
    print("Commit these files:")
    print("  git add assets/icon.ico assets/icon.png assets/icon-512.png")
    print("  git commit -m 'chore: add application icons'")


if __name__ == "__main__":
    generate_icons()