from pathlib import Path

from app.core.config import settings


def list_cityscapes_samples(limit: int = 20) -> list[dict]:
    """
    List sample images from Cityscapes leftImg8bit layout:
    data/cityscapes/leftImg8bit/{train,val,test}/**/*.png
    """
    root = settings.cityscapes_path / "leftImg8bit"
    if not root.exists():
        return []

    samples: list[dict] = []
    for split in ("val", "train", "test"):
        split_dir = root / split
        if not split_dir.exists():
            continue
        for path in sorted(split_dir.rglob("*_leftImg8bit.png")):
            samples.append(
                {
                    "split": split,
                    "path": str(path),
                    "relative_path": str(path.relative_to(settings.cityscapes_path)),
                }
            )
            if len(samples) >= limit:
                return samples
    return samples
