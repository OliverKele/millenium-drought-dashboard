import PIL.Image
PIL.Image.ANTIALIAS = PIL.Image.LANCZOS # Patch for PIL.Image.ANTIALIAS deprecation
from moviepy.editor import VideoFileClip, clips_array

# ---------- Code to Create Side-by-Side Videos ----------

def make_side_by_side(left_path, right_path, output_path, fps=1):
    left_clip = VideoFileClip(left_path)
    right_clip = VideoFileClip(right_path)
    min_height = min(left_clip.h, right_clip.h)
    
    # Ensure height is even
    if min_height % 2 == 1:
        min_height -= 1
    
    left_clip_resized = left_clip.resize(height=min_height)
    right_clip_resized = right_clip.resize(height=min_height)
    
    # Calculate total width and ensure its even 
    total_width = left_clip_resized.w + right_clip_resized.w
    if total_width % 2 == 1:
        right_clip_resized = right_clip_resized.resize(width=right_clip_resized.w - 1)
    
    # Make sure durations match before writing final video
    min_duration = min(left_clip_resized.duration, right_clip_resized.duration)
    left_clip_final = left_clip_resized.subclip(0, min_duration)
    right_clip_final = right_clip_resized.subclip(0, min_duration)
    final_clip = clips_array([[left_clip_final, right_clip_final]])
    final_clip.write_videofile(output_path, fps=fps, codec='libx264', audio_codec='aac')
    print(f"Saved: {output_path}")

# ABARES visualisations for right video
metrics = {
	"Farm Profit": "outputs/animated_farm_profit.mp4",
	"Livestock Count": "outputs/animated_livestock.mp4",
	"Wheat Production": "outputs/animated_wheat.mp4",
}

# Soil moisture used for left video
soil_moisture_1993 = "outputs/soil_moisture_AUS_anom_from1993.mp4"

# Loop through ABARES metrics to create side-by-side videos
for metric, right_video in metrics.items():
	output_path = f"outputs/side_by_side_{metric.replace(' ', '_').lower()}.mp4"
	make_side_by_side(soil_moisture_1993, right_video, output_path, fps=1)
     

