from moviepy import VideoFileClip, ColorClip, CompositeVideoClip, vfx
import os
import numpy as np

try:
    print("Starting solid background video processing...")
    
    # Paths
    base_dir = r"c:\Users\sachi\Downloads\infinitebz---chennai-business-hub (1)"
    video_path = os.path.join(base_dir, "public", "hero-video.mp4")
    output_path = os.path.join(base_dir, "public", "hero-video-processed.mp4") # Overwriting the original processed file name

    print(f"Video path: {video_path}")

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # Load video
    video = VideoFileClip(video_path)
    print(f"Video loaded. Duration: {video.duration}s, Size: {video.size}")
    
    # Auto-detect black bars on sides (Same logic as before)
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
            
    print(f"Detected content horizontal range: {x1} to {x2} (Width: {w})")
    
    if x1 > 10 or x2 < w - 10:
        print(f"Cropping sides: x1={x1}, x2={x2}")
        video = video.cropped(x1=x1, x2=x2)
    
    # Crop bottom watermark
    w, h = video.size
    print(f"Size after side crop: {w}x{h}. Cropping bottom 60 pixels for watermark...")
    video = video.cropped(y2=h-60)
    w, h = video.size
    print(f"Final size: {w}x{h}")

    # Create solid background
    # #0f172a = [15, 23, 42]
    print("Creating solid background #0f172a...")
    bg = ColorClip(size=(w, h), color=[15, 23, 42], duration=video.duration)

    # Apply mask color (make white transparent)
    print("Applying color mask...")
    transparent_video = video.with_effects([vfx.MaskColor(color=[255, 255, 255], threshold=20, stiffness=5)])

    # Composite: Solid BG -> Transparent Video
    print("Compositing video...")
    final_clip = CompositeVideoClip([bg, transparent_video])

    # Write output
    print(f"Writing output to {output_path}...")
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=video.fps or 24)
    
    print("Video processing complete!")

except Exception as e:
    print(f"Error processing video: {str(e)}")
    import traceback
    traceback.print_exc()
