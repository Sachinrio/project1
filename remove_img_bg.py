from rembg import remove
from PIL import Image
import os

def cut_background(input_path, output_path):
    print(f"Processing {input_path}...")
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return
    
    input_image = Image.open(input_path)
    # Remove background
    output_image = remove(input_image)
    # Save as transparent PNG
    output_image.save(output_path, "PNG")
    print(f"Saved transparent image to {output_path}")

if __name__ == "__main__":
    base_dir = r"c:\Users\sachi\Downloads\infinitebz---chennai-business-hub (1)"
    
    # Process Left Image
    left_in = os.path.join(base_dir, "frontend", "public", "media", "left-float.png")
    left_out = os.path.join(base_dir, "frontend", "public", "media", "left-float-transparent.png")
    cut_background(left_in, left_out)
    
    # Process Right Image
    right_in = os.path.join(base_dir, "frontend", "public", "media", "right-float.png")
    right_out = os.path.join(base_dir, "frontend", "public", "media", "right-float-transparent.png")
    cut_background(right_in, right_out)
