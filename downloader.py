#downloader.py
import gdown
import os
import json
from typing import Tuple, Optional
from config import Config

class GoogleDriveDownloader:
    def __init__(self, config: Config):
        self.config = config
        
    def extract_file_id(self, gdrive_url: str) -> str:
        """Extract file ID from Google Drive URL"""
        if '/file/d/' in gdrive_url:
            return gdrive_url.split('/file/d/')[1].split('/')[0]
        elif 'id=' in gdrive_url:
            return gdrive_url.split('id=')[1].split('&')[0]
        else:
            raise ValueError("Invalid Google Drive URL format")
    
    def download_video(self, gdrive_url: str, output_path: str) -> str:
        """Download video from Google Drive"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Check if file already exists
            if os.path.exists(output_path):
                print(f"Video already exists: {output_path}")
                return output_path
            
            file_id = self.extract_file_id(gdrive_url)
            download_url = f"https://drive.google.com/uc?id={file_id}"
            
            print(f"Downloading video from Google Drive...")
            gdown.download(download_url, output_path, quiet=False)
            
            if os.path.exists(output_path):
                print(f"Video downloaded successfully: {output_path}")
                return output_path
            else:
                raise Exception("Download failed - file not found")
                
        except Exception as e:
            print(f"Error downloading video: {e}")
            raise

class StateManager:
    def __init__(self, state_file: str):
        self.state_file = state_file
    
    def load_state(self) -> dict:
        """Load processing state from file"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'current_position': 0,
            'clip_count': 0,
            'last_processed': None
        }
    
    def save_state(self, state: dict):
        """Save processing state to file"""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
