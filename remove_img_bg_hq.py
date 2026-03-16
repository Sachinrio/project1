from rembg import remove
from PIL import Image
import os

def cut_background_high_quality(input_path, output_path):
    print(f"HQ Processing {input_path}...")
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return
    
    input_image = Image.open(input_path).convert("RGBA")
    
    # Remove background with alpha matting for smoother edges
    # alpha_matting=True uses a more sophisticated algorithm for edges
    output_image = remove(
        input_image, 
        alpha_matting=True,
        alpha_matting_foreground_threshold=240,
        alpha_matting_background_threshold=10,
        alpha_matting_erode_size=10
    )
    
    # Save with high quality
    output_image.save(output_path, "PNG", optimize=True)
    print(f"Saved HQ transparent image to {output_path}")

if __name__ == "__main__":
    base_dir = r"c:\Users\sachi\Downloads\infinitebz---chennai-business-hub (1)"
    
    # Process Left Image
    left_in = os.path.join(base_dir, "frontend", "public", "media", "left-float.png")
    left_out = os.path.join(base_dir, "frontend", "public", "media", "left-float-hq.png")
    cut_background_high_quality(left_in, left_out)
    
    # Process Sidebar Image
    sidebar_in = os.path.join(base_dir, "frontend", "media", "Gemini_Generated_Image_y5y6l5y5y6l5y5y6.png")
    sidebar_out = os.path.join(base_dir, "frontend", "public", "media", "sidebar-float-hq.png")
    cut_background_high_quality(sidebar_in, sidebar_out)
