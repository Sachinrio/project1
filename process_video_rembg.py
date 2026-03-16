import os
import numpy as np
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, VideoClip
from rembg import remove
from PIL import Image
from tqdm import tqdm

try:
    print("Starting AI background removal (rembg) processing...")
    
    # Paths
    base_dir = r"c:\Users\sachi\Downloads\infinitebz---chennai-business-hub (1)"
    video_path = os.path.join(base_dir, "public", "hero-video-raw.mp4")
    output_path = os.path.join(base_dir, "public", "hero-video-final.mp4")

    print(f"Input video: {video_path}")
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # Load video
    video = VideoFileClip(video_path)
    # Reducing duration for testing if needed, but we'll try full processing
    # video = video.subclipped(0, 5) 
    print(f"Video loaded. Duration: {video.duration}s, Size: {video.size}, FPS: {video.fps}")

    # --- Auto-Crop Logic (Same as before to remove black bars first) ---
    print("Analyzing for black bars...")
    sample_t = min(1.0, video.duration / 2)
    frame = video.get_frame(sample_t)
    h, w, _ = frame.shape
    mid_y = h // 2
    row = frame[mid_y]
    threshold = 20
    x1 = 0
    for x in range(w):
        if np.max(row[x]) > threshold:
            x1 = x
            break     
    x2 = w
    for x in range(w - 1, -1, -1):
        if np.max(row[x]) > threshold:
            x2 = x + 1
            break
            
    if x1 > 10 or x2 < w - 10:
        print(f"Cropping sides: {x1} to {x2}")
        video = video.cropped(x1=x1, x2=x2)
    
    # Crop bottom watermark (Veo)
    w, h = video.size
    print(f"Cropping bottom watermark. Old height: {h}")
    video = video.cropped(y2=h-60)
    w, h = video.size
    print(f"Final Size: {w}x{h}")

    # --- REMBG Processing ---
    # We need to process each frame. rembg expects PIL image or bytes.
    # moviepy iter_frames yields numpy arrays.
    
    def process_frame(frame_np):
        # Convert numpy (h,w,3) to PIL
        img = Image.fromarray(frame_np)
        
        # Remove background
        # alpha_matting=True can improve edges but is slower. 
        # Using default settings first.
        result = remove(img) 
        
        # Result is RGBA PIL image
        # Convert back to numpy (h,w,4)
        return np.array(result)

    print("Processing frames with rembg (this may take a while)...")
    
    # moviepy's fl_image usually expects 3-channel return if clip is 3-channel.
    # But we need 4-channel (RGBA) for transparency.
    # So we should construct a new ImageSequenceClip or use fl(fun) carefully.
    
    # Better approach: Extract all frames, process them, create new clip.
    # This consumes memory, but for a short loop it might be okay.
    # Or write to a directory of PNGs then stitch.
    
    # Let's try the transformed clip approach.
    # video.fl_image(process_frame) might work if we accept it becomes 4-channel.
    
    processed_frames = []
    # Using tqdm for progress
    for frame in tqdm(video.iter_frames(), total=int(video.duration * video.fps)):
        processed_frames.append(process_frame(frame))
        
    # Create clip from processed frames
    from moviepy import ImageSequenceClip
    transparent_clip = ImageSequenceClip(processed_frames, fps=video.fps)

    # --- Radial Gradient Background ---
    def make_gradient(t):
        y = np.linspace(0, 1, h)[:, None]
        x = np.linspace(0, 1, w)[None, :]
        cx, cy = 0.5, -0.2
        dist = np.sqrt((x-cx)**2 + (y-cy)**2)
        g = np.clip(dist*2, 0, 1)
        c1 = np.array([238, 242, 255]) # #eef2ff
        c2 = np.array([255, 255, 255]) # #ffffff
        img = (c1*(1-g[:,:,None]) + c2*(g[:,:,None])).astype(np.uint8)
        return img

    bg_clip = VideoClip(make_gradient, duration=video.duration)

    # --- Composition ---
    print("Compositing...")
    # Composite: Background -> Transparent Subject
    final_clip = CompositeVideoClip([bg_clip, transparent_clip.with_position("center")])

    # Write output
    print(f"Writing output to {output_path}...")
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=video.fps)
    
    print("Video processing complete!")

except Exception as e:
    print(f"Error processing video: {str(e)}")
    import traceback
    traceback.print_exc()
