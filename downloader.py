import os
import requests
from config import Config

class DropboxDownloader:
    def __init__(self, config: Config):
        self.config = config

    def download_video(self, dropbox_url: str, output_path: str) -> str:
        """Download video from Dropbox direct link"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if os.path.exists(output_path):
                print(f"✅ Video already exists: {output_path}")
                return output_path

            # Ensure URL has dl=1 to force direct download
            if not dropbox_url.endswith("?dl=1"):
                if "?" in dropbox_url:
                    dropbox_url = dropbox_url.split("?")[0] + "?dl=1"
                else:
                    dropbox_url += "?dl=1"

            print("📥 Downloading video from Dropbox...")
            print(f"→ {dropbox_url}")

            with requests.get(dropbox_url, stream=True) as r:
                r.raise_for_status()
                with open(output_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            print(f"✅ Video downloaded successfully: {output_path}")
            return output_path

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
