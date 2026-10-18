import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForSemanticSegmentation

from app.core.config import settings
from app.ml.postprocessing import (
    aggregate_class_counts,
    build_color_palette,
    mask_to_colored_image,
    overlay_on_original,
)
from app.ml.preprocessing import load_image_rgb, resize_for_inference

_processor: AutoImageProcessor | None = None
_model: AutoModelForSemanticSegmentation | None = None
_palette: np.ndarray | None = None


def _get_device() -> torch.device:
    if settings.MODEL_DEVICE == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def load_segformer() -> None:
    global _processor, _model, _palette
    if _model is not None:
        return
    _processor = AutoImageProcessor.from_pretrained(settings.SEGFORMER_MODEL_ID)
    _model = AutoModelForSemanticSegmentation.from_pretrained(settings.SEGFORMER_MODEL_ID)
    _model.to(_get_device())
    _model.eval()
    _palette = build_color_palette()


@dataclass
class InferenceResult:
    segmented_path: str
    overlay_path: str
    class_counts: dict[str, int]
    inference_time_ms: float
    detected_class_count: int


def run_inference_on_image(image_path: str, output_dir: Path, stem: str) -> InferenceResult:
    load_segformer()
    assert _processor is not None and _model is not None and _palette is not None

    output_dir.mkdir(parents=True, exist_ok=True)
    image = resize_for_inference(load_image_rgb(image_path))
    inputs = _processor(images=image, return_tensors="pt")
    inputs = {k: v.to(_get_device()) for k, v in inputs.items()}

    start = time.perf_counter()
    with torch.no_grad():
        outputs = _model(**inputs)
        logits = outputs.logits
        upsampled = torch.nn.functional.interpolate(
            logits,
            size=image.size[::-1],
            mode="bilinear",
            align_corners=False,
        )
        pred = upsampled.argmax(dim=1)[0].cpu().numpy()
    elapsed_ms = (time.perf_counter() - start) * 1000

    mask_rgb = mask_to_colored_image(pred, _palette)
    overlay = overlay_on_original(image, mask_rgb)

    seg_path = output_dir / f"{stem}_segmented.png"
    overlay_path = output_dir / f"{stem}_overlay.png"
    mask_rgb.save(seg_path)
    overlay.save(overlay_path)

    class_counts = aggregate_class_counts(pred)
    return InferenceResult(
        segmented_path=str(seg_path),
        overlay_path=str(overlay_path),
        class_counts=class_counts,
        inference_time_ms=elapsed_ms,
        detected_class_count=len(class_counts),
    )
