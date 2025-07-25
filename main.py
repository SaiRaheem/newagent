import os
from dotenv import load_dotenv
from config import Config
from scheduler import VideoScheduler

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize configuration
    config = Config()
    
    # Video settings - CONFIGURE THESE
    GDRIVE_VIDEO_URL = "https://drive.google.com/file/d/1UVoxrF0UPXo761sPKhxdSySA3mzm6MKv/view?usp=sharing"
 # Replace with your Google Drive URL
    VIDEO_START_TIME = 0      # Start processing from this time (seconds)
    VIDEO_END_TIME = None     # End processing at this time (seconds) - None for full video
    
    # Validate required environment variables
    required_vars = [
        'INSTAGRAM_ACCESS_TOKEN',
        'INSTAGRAM_USER_ID', 
        'CLOUDINARY_CLOUD_NAME',
        'CLOUDINARY_API_KEY',
        'CLOUDINARY_API_SECRET'
    ]
    
    missing_vars = [var for var in required_vars if not getattr(config, var)]
    if missing_vars:
        print("Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these in your .env file or environment")
        return
    
    # Create necessary directories
    os.makedirs(config.DOWNLOAD_PATH, exist_ok=True)
    os.makedirs(config.CLIPS_PATH, exist_ok=True)
    
    try:
        # Initialize and start the scheduler
        scheduler = VideoScheduler(
            config=config,
            gdrive_url=GDRIVE_VIDEO_URL,
            video_start_time=VIDEO_START_TIME,
            video_end_time=VIDEO_END_TIME
        )
        
        # Start the scheduling process
        scheduler.start_scheduling()
        
    except KeyboardInterrupt:
        print("\nScheduler stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()