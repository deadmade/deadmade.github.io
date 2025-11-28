#!/usr/bin/env python3
"""
Favicon Generator for Manuel Schülein Portfolio
Generates a complete favicon set with "MS" initials
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Configuration
OUTPUT_DIR = "static/icons"
ACCENT_COLOR = "#1565c0"  # Site accent color
BACKGROUND_COLOR = "#ffffff"
TEXT_COLOR = "#ffffff"
INITIALS = "M"

# Sizes to generate
SIZES = {
    "favicon-16x16.png": 16,
    "favicon-32x32.png": 32,
    "android-chrome-192x192.png": 192,
    "android-chrome-512x512.png": 512,
    "apple-touch-icon.png": 180,
}

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_favicon(size, initials, bg_color, text_color, output_path):
    """Create a single favicon image with initials in a circle"""
    # Create image with transparency
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Draw circle background
    margin = size // 10
    circle_bbox = [margin, margin, size - margin, size - margin]
    draw.ellipse(circle_bbox, fill=hex_to_rgb(bg_color))

    # Draw initials text
    # Try to use a system font, fallback to default if not available
    try:
        # Try common monospace fonts
        font_size = int(size * 0.7)  # 70% of favicon size (40% increase)
        font = ImageFont.truetype("consola.ttf", font_size)  # Windows
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", size // 2)  # Linux
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", size // 2)  # macOS
            except:
                # Fallback to default font
                font = ImageFont.load_default()

    # Get text bounding box for centering
    bbox = draw.textbbox((0, 0), initials, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Calculate centered position
    x = (size - text_width) // 2 - bbox[0]
    y = (size - text_height) // 2 - bbox[1]

    # Draw text
    draw.text((x, y), initials, fill=hex_to_rgb(text_color), font=font)

    # Save image
    img.save(output_path, "PNG")
    print(f"[OK] Created {output_path}")

def create_ico(source_32, source_16, output_path):
    """Create multi-size ICO file from PNG sources"""
    img_32 = Image.open(source_32)
    img_16 = Image.open(source_16)

    img_32.save(output_path, format='ICO', sizes=[(32, 32), (16, 16)], append_images=[img_16])
    print(f"[OK] Created {output_path}")

def create_svg_favicon(initials, bg_color, text_color, output_path):
    """Create SVG favicon"""
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="45" fill="{bg_color}"/>
  <text x="50" y="50" font-family="monospace" font-size="56" font-weight="bold"
        fill="{text_color}" text-anchor="middle" dominant-baseline="central">{initials}</text>
</svg>'''

    with open(output_path, 'w') as f:
        f.write(svg_content)
    print(f"[OK] Created {output_path}")

def create_safari_pinned_tab(initials, output_path):
    """Create monochrome SVG for Safari pinned tabs"""
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="45" fill="#000"/>
  <text x="50" y="50" font-family="monospace" font-size="56" font-weight="bold"
        fill="#fff" text-anchor="middle" dominant-baseline="central">{initials}</text>
</svg>'''

    with open(output_path, 'w') as f:
        f.write(svg_content)
    print(f"[OK] Created {output_path}")

def create_webmanifest(output_path):
    """Create site.webmanifest for PWA support"""
    manifest_content = '''{
    "name": "Manuel Schülein Portfolio",
    "short_name": "M. Schülein",
    "icons": [
        {
            "src": "/icons/android-chrome-192x192.png",
            "sizes": "192x192",
            "type": "image/png"
        },
        {
            "src": "/icons/android-chrome-512x512.png",
            "sizes": "512x512",
            "type": "image/png"
        }
    ],
    "theme_color": "#1565c0",
    "background_color": "#fafafa",
    "display": "standalone"
}'''

    with open(output_path, 'w') as f:
        f.write(manifest_content)
    print(f"[OK] Created {output_path}")

def create_browserconfig(output_path):
    """Create browserconfig.xml for Windows tiles"""
    config_content = '''<?xml version="1.0" encoding="utf-8"?>
<browserconfig>
    <msapplication>
        <tile>
            <square150x150logo src="/icons/android-chrome-192x192.png"/>
            <TileColor>#1565c0</TileColor>
        </tile>
    </msapplication>
</browserconfig>'''

    with open(output_path, 'w') as f:
        f.write(config_content)
    print(f"[OK] Created {output_path}")

def main():
    """Generate all favicon files"""
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"\nGenerating favicons for '{INITIALS}'...")
    print(f"Output directory: {OUTPUT_DIR}\n")

    # Generate PNG favicons
    for filename, size in SIZES.items():
        output_path = os.path.join(OUTPUT_DIR, filename)
        create_favicon(size, INITIALS, ACCENT_COLOR, TEXT_COLOR, output_path)

    # Generate ICO file
    ico_path = os.path.join(OUTPUT_DIR, "favicon.ico")
    create_ico(
        os.path.join(OUTPUT_DIR, "favicon-32x32.png"),
        os.path.join(OUTPUT_DIR, "favicon-16x16.png"),
        ico_path
    )

    # Generate SVG favicon
    svg_path = os.path.join(OUTPUT_DIR, "favicon.svg")
    create_svg_favicon(INITIALS, ACCENT_COLOR, TEXT_COLOR, svg_path)

    # Generate Safari pinned tab SVG
    safari_svg_path = os.path.join(OUTPUT_DIR, "safari-pinned-tab.svg")
    create_safari_pinned_tab(INITIALS, safari_svg_path)

    # Generate webmanifest
    manifest_path = os.path.join(OUTPUT_DIR, "site.webmanifest")
    create_webmanifest(manifest_path)

    # Generate browserconfig
    browserconfig_path = os.path.join(OUTPUT_DIR, "browserconfig.xml")
    create_browserconfig(browserconfig_path)

    print(f"\n[SUCCESS] All favicons generated successfully in {OUTPUT_DIR}/\n")

if __name__ == "__main__":
    main()
