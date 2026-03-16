from moviepy import VideoFileClip, VideoClip, CompositeVideoClip, vfx
import os
import numpy as np

try:
    print("Starting radial gradient video processing...")
    
    # Paths
    base_dir = r"c:\Users\sachi\Downloads\infinitebz---chennai-business-hub (1)"
    video_path = os.path.join(base_dir, "public", "hero-video-raw.mp4")
    output_path = os.path.join(base_dir, "public", "hero-video-radial.mp4")

    print(f"Video path: {video_path}")

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # Load video
    video = VideoFileClip(video_path)
    print(f"Video loaded. Duration: {video.duration}s, Size: {video.size}")
    
    # --- Auto-Crop Logic (from previous scripts) ---
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
            
    print(f"Detected content: {x1} to {x2}")
    if x1 > 10 or x2 < w - 10:
        video = video.cropped(x1=x1, x2=x2)
    
    # Crop bottom watermark
    w, h = video.size
    video = video.cropped(y2=h-60)
    w, h = video.size
    print(f"Final Size for gradient: {w}x{h}")

    # --- Masking White Background ---
    # We must make the white background transparent so the gradient shows through
    print("Applying color mask...")
    transparent_video = video.with_effects([vfx.MaskColor(color=[255, 255, 255], threshold=20, stiffness=5)])

    # --- User's Gradient Logic ---
    def make_gradient(t):
        # We need to generate an image of size (h, w, 3)
        # Note: numpy meshgrid or broadcasting
        
        # Grid for broadcasting
        # y: (h, 1)
        y = np.linspace(0, 1, h)[:, None]
        # x: (1, w)
        x = np.linspace(0, 1, w)[None, :]
        
        # User parameters
        cx, cy = 0.5, -0.2
        dist = np.sqrt((x-cx)**2 + (y-cy)**2)
        
        # g is 0 to 1
        g = np.clip(dist*2, 0, 1)
        
        # Colors
        c1 = np.array([238, 242, 255]) # #eef2ff
        c2 = np.array([255, 255, 255]) # #ffffff
        
        # Interpolate
        # g[:,:,None] shape is (h, w, 1)
        # c1 shape is (3,)
        # Result (h, w, 3)
        img = (c1*(1-g[:,:,None]) + c2*(g[:,:,None])).astype(np.uint8)
        return img

    print("Generating radial gradient background...")
    # Create a VideoClip that generates frames using make_gradient
    # Ideally we make one image duration, but make_gradient accepts 't' so it's a dynamic clip generator
    # Since gradient is static, we can optimize by making one ImageClip, but VideoClip is fine.
    # Actually, fl_image is for transforming an existing clip. 
    # To create a new background clip from scratch:
    bg = VideoClip(make_gradient, duration=video.duration)
    
    # --- Composition ---
    print("Compositing...")
    # Video centered? It should be same size, but set_position('center') is safe
    final_clip = CompositeVideoClip([bg, transparent_video.with_position("center")])

    # Write output
    print(f"Writing output to {output_path}...")
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=video.fps or 24)
    
    print("Video processing complete!")

except Exception as e:
    print(f"Error processing video: {str(e)}")
    import traceback
    traceback.print_exc()
