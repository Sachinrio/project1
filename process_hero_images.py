from rembg import remove
from PIL import Image
import os

def process_image(input_path, output_path):
    print(f"Processing {input_path}...")
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        return

    try:
        input_image = Image.open(input_path).convert("RGBA")
        output_image = remove(
            input_image, 
            alpha_matting=True,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10,
            alpha_matting_erode_size=10
        )
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        output_image.save(output_path, "PNG", optimize=True)
        print(f"Successfully saved to {output_path}")
    except Exception as e:
        print(f"Failed to process {input_path}: {e}")

if __name__ == "__main__":
    base_dir = r"c:\Users\sachi\Downloads\infinitebz---chennai-business-hub (1)"
    
    # Define source and destination
    # Left Image: Gemini_Generated_Image_lfpz9plfpz9plfpz
    left_src = os.path.join(base_dir, "frontend", "media", "Gemini_Generated_Image_lfpz9plfpz9plfpz.png")
    left_dest = os.path.join(base_dir, "frontend", "public", "media", "left-float-gemini.png")
    
    # Right Image: Gemini_Generated_Image_9hide19hide19hid
    right_src = os.path.join(base_dir, "frontend", "media", "Gemini_Generated_Image_9hide19hide19hid.png")
    right_dest = os.path.join(base_dir, "frontend", "public", "media", "right-float-gemini.png")

    print("Starting background removal...")
    process_image(left_src, left_dest)
    process_image(right_src, right_dest)
    print("Processing complete.")
