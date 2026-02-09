from moviepy import VideoFileClip, vfx
import os
import numpy as np

try:
    print("Starting transparent video processing...")
    
    # Paths
    base_dir = r"c:\Users\sachi\Downloads\infinitebz---chennai-business-hub (1)"
    video_path = os.path.join(base_dir, "public", "hero-video.mp4")
    output_path = os.path.join(base_dir, "public", "hero-video-transparent.webm")

    print(f"Video path: {video_path}")

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # Load video
    video = VideoFileClip(video_path)
    print(f"Video loaded. Duration: {video.duration}s, Size: {video.size}")
    
    # Auto-detect black bars on sides
    sample_t = min(1.0, video.duration / 2)
    frame = video.get_frame(sample_t)
    h, w, _ = frame.shape
    
    # Analyze middle row for non-black pixels
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
    
    # Apply side crops if significant
    if x1 > 10 or x2 < w - 10:
        print(f"Cropping sides: x1={x1}, x2={x2}")
        video = video.cropped(x1=x1, x2=x2)
    
    # Crop bottom watermark (Veo)
    w, h = video.size
    print(f"Size after side crop: {w}x{h}. Cropping bottom 60 pixels for watermark...")
    video = video.cropped(y2=h-60)
    w, h = video.size
    print(f"Final size: {w}x{h}")

    # Apply mask color (make white transparent)
    # Using 'stiffness' as discovered in previous attempts for moviepy v2
    print("Applying color mask for transparency...")
    # High threshold to catch off-whites, stiffness to smooth edges
    transparent_video = video.with_effects([vfx.MaskColor(color=[255, 255, 255], threshold=20, stiffness=5)])

    # Write output as WebM with VP9 code for alpha channel support
    print(f"Writing output to {output_path}...")
    # bitrate argument is optional but good for quality. 'auto' or specific value.
    # pixel_format='yuva420p' allows alpha channel in ffmpeg for some codecs, 
    # but for libvpx-vp9, the alpha is handled by the codec.
    transparent_video.write_videofile(
        output_path, 
        codec="libvpx-vp9",
        audio_codec="libvorbis", # or 'libopus'
        fps=video.fps or 24,
        # preset='ultrafast' can speed up testing, but 'good' or default is better for quality
    )
    
    print("Video processing complete!")

except Exception as e:
    print(f"Error processing video: {str(e)}")
    import traceback
    traceback.print_exc()
