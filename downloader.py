import os
import requests

class DropboxDownloader:
    def download_video(self, dropbox_url: str, output_path: str):
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Convert to direct download
            if "?dl=1" not in dropbox_url:
                dropbox_url = dropbox_url.split("?")[0] + "?dl=1"

            print(f"\n📥 Downloading video from Dropbox...\n→ {dropbox_url}")
            response = requests.get(dropbox_url)

            if response.status_code != 200:
                raise Exception(f"Failed to download video. Status code: {response.status_code}")

            with open(output_path, "wb") as f:
                f.write(response.content)

            print(f"✅ Video downloaded successfully: {output_path}")

        except Exception as e:
            print(f"❌ Error downloading video: {e}")
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
