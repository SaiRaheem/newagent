# uploader.py
import cloudinary
import cloudinary.uploader
import requests
import json
import time
from typing import Optional, Dict, Any
from config import Config

class CloudinaryUploader:
    def __init__(self, config: Config):
        self.config = config
        cloudinary.config(
            cloud_name=config.CLOUDINARY_CLOUD_NAME,
            api_key=config.CLOUDINARY_API_KEY,
            api_secret=config.CLOUDINARY_API_SECRET
        )
    
    def upload_video(self, video_path: str, public_id: Optional[str] = None) -> Dict[str, Any]:
        """Upload video to Cloudinary"""
        try:
            result = cloudinary.uploader.upload(
                video_path,
                resource_type="video",
                public_id=public_id,
                chunk_size=6000000,  # 6MB chunks for large files
                eager=[
                    {"quality": "auto", "fetch_format": "mp4"}
                ]
            )
            print(f"Video uploaded to Cloudinary: {result['secure_url']}")
            return result
        except Exception as e:
            print(f"Error uploading to Cloudinary: {e}")
            raise

class InstagramUploader:
    def __init__(self, config: Config):
        self.config = config
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def upload_video(self, video_url: str, caption: str = "") -> bool:
        """Upload video to Instagram using Graph API"""
        try:
            # Step 1: Create media container
            container_url = f"{self.base_url}/{self.config.INSTAGRAM_USER_ID}/media"
            container_params = {
                'media_type': 'VIDEO',
                'video_url': video_url,
                'caption': caption,
                'access_token': self.config.INSTAGRAM_ACCESS_TOKEN
            }
            
            container_response = requests.post(container_url, data=container_params)
            container_data = container_response.json()
            
            if 'id' not in container_data:
                print(f"Error creating container: {container_data}")
                return False
            
            creation_id = container_data['id']
            print(f"Media container created: {creation_id}")
            
            # Step 2: Check upload status
            status_url = f"{self.base_url}/{creation_id}"
            status_params = {
                'fields': 'status_code',
                'access_token': self.config.INSTAGRAM_ACCESS_TOKEN
            }
            
            # Wait for video processing
            max_attempts = 30
            for attempt in range(max_attempts):
                time.sleep(10)  # Wait 10 seconds between checks
                status_response = requests.get(status_url, params=status_params)
                status_data = status_response.json()
                
                if status_data.get('status_code') == 'FINISHED':
                    print("Video processing completed")
                    break
                elif status_data.get('status_code') == 'ERROR':
                    print(f"Video processing failed: {status_data}")
                    return False
                else:
                    print(f"Processing... Status: {status_data.get('status_code', 'UNKNOWN')}")
            
            # Step 3: Publish the media
            publish_url = f"{self.base_url}/{self.config.INSTAGRAM_USER_ID}/media_publish"
            publish_params = {
                'creation_id': creation_id,
                'access_token': self.config.INSTAGRAM_ACCESS_TOKEN
            }
            
            publish_response = requests.post(publish_url, data=publish_params)
            publish_data = publish_response.json()
            
            if 'id' in publish_data:
                print(f"Video published successfully: {publish_data['id']}")
                return True
            else:
                print(f"Error publishing video: {publish_data}")
                return False
                
        except Exception as e:
            print(f"Error uploading to Instagram: {e}")
            return False
