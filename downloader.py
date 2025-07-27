import os
import json
import gdown
import re
from config import Config

class GoogleDriveDownloader:
    def __init__(self, config: Config):
        self.config = config

    def extract_file_id(self, gdrive_url: str) -> str:
        match = re.search(r'(?:/d/|id=)([a-zA-Z0-9_-]+)', gdrive_url)
        if match:
            return match.group(1)
        raise ValueError("Could not extract file ID from Google Drive URL")

    def download_video(self, gdrive_url: str, output_path: str) -> str:
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            if os.path.exists(output_path):
                print(f"✅ Video already exists: {output_path}")
                return output_path

            file_id = self.extract_file_id(gdrive_url)
            download_url = f"https://drive.google.com/uc?id={file_id}"

            print(f"Downloading video from Google Drive...\n→ {download_url}")
            gdown.download(download_url, output_path, quiet=False, fuzzy=True)

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
