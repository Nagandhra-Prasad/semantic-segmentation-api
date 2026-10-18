from pathlib import Path

import imageio.v2 as imageio
import numpy as np
from PIL import Image


def frames_to_mp4(image_paths: list[str], output_path: Path, fps: float = 8.0) -> str:
    """Encode overlay PNGs to H.264 MP4 (browser-safe)."""
    if not image_paths:
        raise ValueError("No frames to encode")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    frames: list[np.ndarray] = []
    target_size: tuple[int, int] | None = None

    for path in image_paths:
        with Image.open(path) as img:
            rgb = img.convert("RGB")
            if target_size is None:
                target_size = rgb.size
            elif rgb.size != target_size:
                rgb = rgb.resize(target_size, Image.Resampling.BILINEAR)
            frames.append(np.asarray(rgb, dtype=np.uint8))

    with imageio.get_writer(
        str(output_path),
        fps=fps,
        codec="libx264",
        pixelformat="yuv420p",
        macro_block_size=1,
    ) as writer:
        for frame in frames:
            writer.append_data(frame)

    return str(output_path)
