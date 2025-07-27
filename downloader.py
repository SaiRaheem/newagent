import re
import gdown
import os
from config import Config

class GoogleDriveDownloader:
    def __init__(self, config: Config):
        self.config = config

    def download_video(self, gdrive_url: str, output_path: str) -> str:
        """Download video from Google Drive using gdown with file ID"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if os.path.exists(output_path):
                print(f"Video already exists: {output_path}")
                return output_path

            print(f"\n📥 Downloading video from Google Drive...")
            
            # Extract file ID using regex
            match = re.search(r"/d/([a-zA-Z0-9_-]+)", gdrive_url)
            if not match:
                raise ValueError("Invalid Google Drive URL format.")
            file_id = match.group(1)
            print(f"→ File ID: {file_id}")

            # Use file ID with gdown
            gdown.download(id=file_id, output=output_path, quiet=False)

            if os.path.exists(output_path):
                print(f"✅ Video downloaded successfully: {output_path}")
                return output_path
            else:
                raise Exception("Download failed - file not found")

        except Exception as e:
            print(f"❌ Error downloading video: {e}")
            raise



# ⬇️ Don't forget this part:
class StateManager:
    def __init__(self, state_file: str):
        self.state_file = state_file

    def load_state(self) -> dict:
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {'current_position': 0, 'clip_count': 0, 'last_processed': None}

    def save_state(self, state: dict):
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
