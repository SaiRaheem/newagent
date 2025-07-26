import os
import requests
import json
from config import Config

class GoogleDriveDownloader:  # Rename if needed
    def __init__(self, config: Config):
        self.config = config

    def download_video(self, url: str, output_path: str) -> str:
        """Download video from Dropbox or direct URL"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if os.path.exists(output_path):
                print(f"Video already exists: {output_path}")
                return output_path

            print(f"Downloading video from URL: {url}")
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(output_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

            print(f"Video downloaded successfully: {output_path}")
            return output_path

        except Exception as e:
            print(f"Error downloading video: {e}")
            raise

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
