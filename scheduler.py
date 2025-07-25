import os
import scheduler
import time
import threading
from datetime import datetime
from config import Config
from downloader import GoogleDriveDownloader, StateManager
from processor import VideoProcessor
from uploader import CloudinaryUploader, InstagramUploader

class VideoScheduler:
    def __init__(self, config: Config, gdrive_url: str, video_start_time: float = 0, video_end_time: float = None):
        self.config = config
        self.gdrive_url = gdrive_url
        self.video_start_time = video_start_time
        self.video_end_time = video_end_time
        
        # Initialize components
        self.downloader = GoogleDriveDownloader(config)
        self.processor = VideoProcessor(config)
        self.cloudinary_uploader = CloudinaryUploader(config)
        self.instagram_uploader = InstagramUploader(config)
        self.state_manager = StateManager(config.STATE_FILE)
        
        # Video file path
        self.video_file_path = os.path.join(config.DOWNLOAD_PATH, "main_video.mp4")
        
        # Download video once at initialization
        self._download_video_once()
    
    def _download_video_once(self):
        """Download the video file once during initialization"""
        try:
            print("Downloading video from Google Drive...")
            self.downloader.download_video(self.gdrive_url, self.video_file_path)
            
            # Get video duration and set end time if not specified
            video_duration = self.processor.get_video_duration(self.video_file_path)
            if self.video_end_time is None:
                self.video_end_time = video_duration
            else:
                self.video_end_time = min(self.video_end_time, video_duration)
            
            print(f"Video duration: {video_duration}s")
            print(f"Processing range: {self.video_start_time}s - {self.video_end_time}s")
            
        except Exception as e:
            print(f"Failed to download video: {e}")
            raise
    
    def process_next_clip(self):
        """Process and upload the next video clip"""
        try:
            print(f"\n{'='*50}")
            print(f"Processing started at: {datetime.now()}")
            
            # Load current state
            state = self.state_manager.load_state()
            current_position = max(state['current_position'], self.video_start_time)
            clip_count = state['clip_count']
            
            # Check if we've reached the end
            if current_position >= self.video_end_time:
                print("Reached end of video processing range")
                return
            
            # Calculate clip times
            start_time, end_time, has_more = self.processor.calculate_next_clip_times(
                current_position, self.config.CLIP_DURATION, self.video_end_time
            )
            
            print(f"Creating clip {clip_count + 1}: {start_time}s - {end_time}s")
            
            # Generate clip filename
            clip_filename = self.processor.generate_clip_filename(clip_count + 1, start_time, end_time)
            clip_path = os.path.join(self.config.CLIPS_PATH, clip_filename)
            
            # Create clip
            self.processor.trim_video_clip(self.video_file_path, start_time, end_time, clip_path)
            
            # Upload to Cloudinary
            cloudinary_result = self.cloudinary_uploader.upload_video(
                clip_path, 
                public_id=f"video_clip_{clip_count + 1}"
            )
            
            # Create caption
            caption = f"Video clip {clip_count + 1} ({int(start_time)}s - {int(end_time)}s) #video #content"
            
            # Upload to Instagram
            success = self.instagram_uploader.upload_video(
                cloudinary_result['secure_url'], 
                caption
            )
            
            if success:
                print("Successfully uploaded to Instagram!")
                
                # Update state
                new_state = {
                    'current_position': end_time,
                    'clip_count': clip_count + 1,
                    'last_processed': datetime.now().isoformat()
                }
                self.state_manager.save_state(new_state)
                
                # Clean up local clip file
                if os.path.exists(clip_path):
                    os.remove(clip_path)
                    print(f"Cleaned up local file: {clip_path}")
                
            else:
                print("Failed to upload to Instagram")
            
            print(f"Processing completed at: {datetime.now()}")
            print(f"{'='*50}\n")
            
        except Exception as e:
            print(f"Error processing clip: {e}")
            import traceback
            traceback.print_exc()
    
    def start_scheduling(self):
        """Start the hourly scheduling"""
        print("Starting video processing scheduler...")
        print(f"Clip duration: {self.config.CLIP_DURATION} seconds")
        print(f"Sleep interval: {self.config.SLEEP_INTERVAL} seconds ({self.config.SLEEP_INTERVAL/3600} hours)")
        
        # Schedule the job to run every hour
        schedule.every().hour.do(self.process_next_clip)
        
        # Run once immediately
        print("Processing first clip immediately...")
        self.process_next_clip()
        
        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute