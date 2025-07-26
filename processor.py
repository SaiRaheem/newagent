from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import lum_contrast, colorx, fadein, fadeout
import os
import time
import numpy as np
from datetime import datetime
from typing import Tuple
from config import Config

class VideoProcessor:
    def __init__(self, config: Config):
        self.config = config

    def get_video_duration(self, video_path: str) -> float:
        """Get total duration of video in seconds"""
        with VideoFileClip(video_path) as video:
            return video.duration

    def trim_video_clip(self, video_path: str, start_time: float, end_time: float, output_path: str) -> str:
        """Trim and enhance video clip from start_time to end_time"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with VideoFileClip(video_path) as video:
                # Ensure we don't exceed video duration
                actual_end_time = min(end_time, video.duration)

                if start_time >= actual_end_time:
                    raise ValueError(f"Start time {start_time} is beyond video duration {video.duration}")

                # Clip the video
                clip = video.subclip(start_time, actual_end_time)

                # Brightness adjustment (1.9x)
                clip = clip.fl_image(lambda frame: np.clip(frame * 1.9, 0, 255).astype('uint8'))

                # Contrast enhancement
                clip = lum_contrast(clip, contrast=60, lum=0)

                # Saturation enhancement (2x)
                clip = colorx(clip, 2.0)

                # Fade in and out
                clip = fadein(clip, 1.0)     # 1 sec fade in
                clip = fadeout(clip, 1.0)    # 1 sec fade out

                # Vignette effect (basic radial darkening)
                def vignette_effect(get_frame, t):
                    frame = get_frame(t)
                    h, w = frame.shape[:2]
                    Y, X = np.ogrid[:h, :w]
                    center_x, center_y = w / 2, h / 2
                    dist_from_center = ((X - center_x)**2 + (Y - center_y)**2)**0.5
                    mask = np.clip(1 - (dist_from_center / max(w, h)) * 0.4, 0.6, 1)
                    vignette = np.dstack([mask] * 3)
                    return (frame * vignette).astype('uint8')

                clip = clip.fl(vignette_effect)

                # Export the final processed video
                clip.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile='temp-audio.m4a',
                    remove_temp=True,
                    verbose=False,
                    logger=None
                )

            print(f"✅ Clip created: {output_path} ({start_time}s - {actual_end_time}s)")
            return output_path

        except Exception as e:
            print(f"❌ Error creating clip: {e}")
            raise

    def calculate_next_clip_times(self, current_position: float, clip_duration: int, video_duration: float) -> Tuple[float, float, bool]:
        """Calculate start and end times for next clip"""
        start_time = current_position
        end_time = min(current_position + clip_duration, video_duration)
        has_more = end_time < video_duration
        return start_time, end_time, has_more

    def generate_clip_filename(self, clip_count: int, start_time: float, end_time: float) -> str:
        """Generate filename for clip"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"clip_{clip_count:03d}_{timestamp}_{int(start_time)}s-{int(end_time)}s.mp4"
