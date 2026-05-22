import urllib.request
import re
import os
import glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def download_font(font_path):
    print("Fetching font stylesheet...")
    css_url = "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@800"
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(css_url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            match = re.search(r'url\((https://fonts.gstatic.com/s/[^)]+\.ttf)\)', html)
            if match:
                ttf_url = match.group(1)
                print(f"Downloading TTF from: {ttf_url}")
                urllib.request.urlretrieve(ttf_url, font_path)
                return True
            else:
                raise Exception("Could not find TTF URL.")
    except Exception as e:
        print(f"Error downloading font: {e}")
        fallback_url = "https://github.com/google/fonts/raw/main/ofl/plusjakartasans/PlusJakartaSans%5Bwght%5D.ttf"
        try:
            print("Trying fallback font download...")
            urllib.request.urlretrieve(fallback_url, font_path)
            return True
        except Exception as fe:
            print(f"Fallback failed: {fe}")
            return False

def draw_logo_on_image(base_img, font_path, font_size_target=54, text_y_offset=0):
    # Create high-res draw context
    size = base_img.size[0]
    
    # We will work on a high-res scale (x2) to keep text extremely crisp
    scale_factor = 2
    draw_w, draw_h = size * scale_factor, size * scale_factor
    temp_img = base_img.resize((draw_w, draw_h), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(temp_img)
    
    font_size = font_size_target * scale_factor
    font = ImageFont.truetype(font_path, font_size)
    scale = font_size / 24.0
    
    part1 = "Kitch·"
    part2 = "\u0131"  # dotless i
    
    # Measure dimensions
    total_w = draw.textlength("Kitch\u00b7\u0131o", font=font)
    w1 = draw.textlength(part1, font=font)
    
    # Measure exact dotless-i glyph coordinates for exact terracotta dot centering
    mask_i = font.getmask(part2)
    bbox_i = mask_i.getbbox()
    if bbox_i:
        i_left, i_top, i_right, i_bottom = bbox_i
    else:
        i_left, i_top, i_right, i_bottom = 0, 0, 10, 30
        
    i_center_x = w1 + (i_left + i_right) / 2.0
    
    # Center text horizontally and vertically
    ascent, descent = font.getmetrics()
    height = ascent + descent
    
    start_x = (draw_w - total_w) / 2.0
    # Apply vertical offset if specified
    start_y = (draw_h - height) / 2.0 + (text_y_offset * scale_factor)
    y_text_origin = start_y + ascent
    
    # 1. Draw rich drop shadow for high contrast on glowing backgrounds
    shadow_offset_y = int(3 * scale_factor)
    shadow_offset_x = int(1 * scale_factor)
    shadow_color = (0, 0, 0, 220)
    
    # Soft blurred shadow layer
    shadow_layer = Image.new("RGBA", (draw_w, draw_h), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    
    # Draw shadow text
    shadow_draw.text(
        (start_x + shadow_offset_x, y_text_origin + shadow_offset_y),
        "Kitch\u00b7\u0131o",
        fill=shadow_color,
        font=font
    )
    
    # Soft blur the shadow
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=3 * scale_factor))
    temp_img = Image.alpha_composite(temp_img, shadow_layer)
    
    # 2. Draw sharp white brand text
    draw = ImageDraw.Draw(temp_img)
    draw.text(
        (start_x, y_text_origin),
        "Kitch\u00b7\u0131o",
        fill=(255, 255, 255, 255),
        font=font
    )
    
    # 3. Draw terracotta dot with custom neon glow
    dot_center_x = start_x + i_center_x
    i_glyph_top = y_text_origin + i_top
    
    accent_color = (215, 107, 70, 255)       # #D76B46
    glow_color = (215, 107, 70, 180)
    
    dot_radius = (6.0 * scale) / 2.0
    gap = 2.0 * scale
    dot_center_y = i_glyph_top - dot_radius - gap
    
    # Glow layer for dot
    glow_layer = Image.new("RGBA", (draw_w, draw_h), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    glow_spread = 6.0 * scale_factor
    
    glow_draw.ellipse(
        [
            dot_center_x - dot_radius - glow_spread,
            dot_center_y - dot_radius - glow_spread,
            dot_center_x + dot_radius + glow_spread,
            dot_center_y + dot_radius + glow_spread
        ],
        fill=glow_color
    )
    
    blurred_glow = glow_layer.filter(ImageFilter.GaussianBlur(radius=4 * scale_factor))
    temp_img = Image.alpha_composite(temp_img, blurred_glow)
    
    # Draw solid terracotta dot
    draw = ImageDraw.Draw(temp_img)
    draw.ellipse(
        [
            dot_center_x - dot_radius,
            dot_center_y - dot_radius,
            dot_center_x + dot_radius,
            dot_center_y + dot_radius
        ],
        fill=accent_color
    )
    
    # Resize back to original size with high quality lanczos interpolation
    final_img = temp_img.resize((size, size), Image.Resampling.LANCZOS)
    return final_img

def generate_all_logos():
    artifact_dir = r"C:\Users\Safwan\AppData\Local\Temp" # Fallback
    # Detect the actual artifact directory from current context
    possible_dir = r"C:\Users\Safwan\.gemini\antigravity-ide\brain\21f08286-1fe2-4015-95fd-e23e5033f29e"
    if os.path.exists(possible_dir):
        artifact_dir = possible_dir
        
    print(f"Artifact directory: {artifact_dir}")
    
    font_path = "PlusJakartaSans-ExtraBold.ttf"
    if not download_font(font_path):
        print("Failed to download font.")
        return False
        
    # --- OPTION A: GLASSMORPHIC SHIELD (USING BG A) ---
    print("Generating Option A...")
    bg_a_pattern = os.path.join(artifact_dir, "kitchio_bg_a_*.png")
    bg_a_files = glob.glob(bg_a_pattern)
    
    if bg_a_files:
        bg_a_path = bg_a_files[0]
        print(f"Found Background A at: {bg_a_path}")
        bg_a = Image.open(bg_a_path).convert("RGBA")
        # Text centered, slightly larger font size for Option A
        opt_a_img = draw_logo_on_image(bg_a, font_path, font_size_target=52, text_y_offset=0)
    else:
        print("Background A not found, using dark fallback canvas")
        fallback_a = Image.new("RGBA", (512, 512), (12, 10, 9, 255))
        opt_a_img = draw_logo_on_image(fallback_a, font_path, font_size_target=52, text_y_offset=0)
        
    # --- OPTION B: METALLIC SQUIRCLE (USING BG B) ---
    print("Generating Option B...")
    bg_b_pattern = os.path.join(artifact_dir, "kitchio_bg_b_*.png")
    bg_b_files = glob.glob(bg_b_pattern)
    
    if bg_b_files:
        bg_b_path = bg_b_files[0]
        print(f"Found Background B at: {bg_b_path}")
        bg_b = Image.open(bg_b_path).convert("RGBA")
        opt_b_img = draw_logo_on_image(bg_b, font_path, font_size_target=48, text_y_offset=0)
    else:
        print("Background B not found, using dark fallback canvas")
        fallback_b = Image.new("RGBA", (512, 512), (12, 10, 9, 255))
        opt_b_img = draw_logo_on_image(fallback_b, font_path, font_size_target=48, text_y_offset=0)
        
    # --- OPTION C: MINIMALIST FLAT VECTOR EMBLEM (PIL DRAWN FROM SCRATCH) ---
    print("Generating Option C...")
    # Make deep radial gradient backdrop
    opt_c_canvas = Image.new("RGBA", (512, 512), (12, 10, 9, 255))
    c_draw = ImageDraw.Draw(opt_c_canvas)
    
    # Draw premium radial gradient ring manually
    center_x, center_y = 256, 256
    for r in range(210, 206, -1):
        # Muted terracotta outer ring
        alpha = int(255 * ((r - 206) / 4.0))
        c_draw.ellipse(
            [center_x - r, center_y - r, center_x + r, center_y + r],
            outline=(215, 107, 70, alpha),
            width=2
        )
        
    # Inner dark plate
    c_draw.ellipse(
        [center_x - 204, center_y - 204, center_x + 204, center_y + 204],
        fill=(22, 18, 16, 255)
    )
    
    opt_c_img = draw_logo_on_image(opt_c_canvas, font_path, font_size_target=48, text_y_offset=0)
    
    # Save in workspace
    opt_a_img.save("kitchio_profile_val_a.png", "PNG")
    opt_b_img.save("kitchio_profile_val_b.png", "PNG")
    opt_c_img.save("kitchio_profile_val_c.png", "PNG")
    
    # Save the selected best one (Option A - Glassmorphic Shield) as the primary profile logo
    opt_a_img.save("kitchio_profile_logo.png", "PNG")
    
    # Also save them directly in the artifact directory so they are visible in markdown
    opt_a_img.save(os.path.join(artifact_dir, "kitchio_profile_val_a.png"), "PNG")
    opt_b_img.save(os.path.join(artifact_dir, "kitchio_profile_val_b.png"), "PNG")
    opt_c_img.save(os.path.join(artifact_dir, "kitchio_profile_val_c.png"), "PNG")
    opt_a_img.save(os.path.join(artifact_dir, "kitchio_profile_logo.png"), "PNG")
    
    print("All square logo variations successfully generated and saved!")
    
    # Cleanup font
    if os.path.exists(font_path):
        os.remove(font_path)
        
    return True

if __name__ == "__main__":
    generate_all_logos()
