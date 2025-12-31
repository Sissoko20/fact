import base64
from pathlib import Path

def image_to_base64(path):
    image_path = Path(path)
    if not image_path.exists():
        return ""
    return base64.b64encode(image_path.read_bytes()).decode("utf-8")
