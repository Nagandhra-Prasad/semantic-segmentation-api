import numpy as np
from PIL import Image

from app.ml.cityscapes_labels import (
    CITYSCAPES_TRAIN_ID_TO_NAME,
    DISPLAY_CATEGORIES,
)


def build_color_palette() -> np.ndarray:
    """Map each Cityscapes trainId to an RGB colour for visualization."""
    palette = np.zeros((256, 3), dtype=np.uint8)
    name_to_display = {c.key: c.color_rgb for c in DISPLAY_CATEGORIES}
    label_to_key: dict[str, str] = {}
    for cat in DISPLAY_CATEGORIES:
        for label in cat.cityscapes_labels:
            if cat.key == "lane_markings":
                continue
            label_to_key[label] = cat.key

    for train_id, name in CITYSCAPES_TRAIN_ID_TO_NAME.items():
        key = label_to_key.get(name, "road")
        palette[train_id] = name_to_display.get(key, (128, 64, 128))

    return palette


def mask_to_colored_image(prediction: np.ndarray, palette: np.ndarray) -> Image.Image:
    colored = palette[prediction.astype(np.uint8)]
    return Image.fromarray(colored, mode="RGB")


def overlay_on_original(original: Image.Image, mask_rgb: Image.Image, alpha: float = 0.45) -> Image.Image:
    original = original.resize(mask_rgb.size, Image.Resampling.BILINEAR)
    blend = Image.blend(original, mask_rgb, alpha=alpha)
    return blend


def aggregate_class_counts(prediction: np.ndarray) -> dict[str, int]:
    counts: dict[str, int] = {c.key: 0 for c in DISPLAY_CATEGORIES}
    unique, freq = np.unique(prediction, return_counts=True)
    for train_id, pixel_count in zip(unique, freq, strict=False):
        name = CITYSCAPES_TRAIN_ID_TO_NAME.get(int(train_id))
        if not name:
            continue
        for cat in DISPLAY_CATEGORIES:
            if name in cat.cityscapes_labels and cat.key != "lane_markings":
                counts[cat.key] += int(pixel_count)
                break
    return {k: v for k, v in counts.items() if v > 0}
