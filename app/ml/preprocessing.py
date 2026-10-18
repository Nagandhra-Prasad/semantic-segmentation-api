import numpy as np
from PIL import Image


def load_image_rgb(path: str) -> Image.Image:
    image = Image.open(path).convert("RGB")
    return image


def resize_for_inference(image: Image.Image, max_side: int = 1024) -> Image.Image:
    w, h = image.size
    scale = min(max_side / max(w, h), 1.0)
    if scale < 1.0:
        image = image.resize((int(w * scale), int(h * scale)), Image.Resampling.BILINEAR)
    return image


def normalize_image_array(rgb: np.ndarray) -> np.ndarray:
    return rgb.astype(np.float32) / 255.0
