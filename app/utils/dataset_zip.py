import zipfile
from pathlib import Path

from fastapi import HTTPException, status

from app.core.config import settings


def _is_image_path(path: Path) -> bool:
    return path.suffix.lower() in settings.allowed_image_exts


def extract_dataset_zip(zip_path: Path, dest_dir: Path) -> list[str]:
    """Extract a zip and return sorted image file paths (relative limits applied later)."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                name = Path(info.filename)
                if name.parts and name.parts[0].startswith("__MACOSX"):
                    continue
                if ".." in name.parts:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid path inside zip archive",
                    )
            zf.extractall(dest_dir)
    except zipfile.BadZipFile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is not a valid zip archive",
        ) from None

    images: list[Path] = []
    for path in sorted(dest_dir.rglob("*")):
        if path.is_file() and _is_image_path(path):
            images.append(path)

    if not images:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Zip must contain at least one image (jpg, png, webp, bmp)",
        )

    limit = settings.DATASET_MAX_IMAGES
    selected = images[:limit]
    return [str(p) for p in selected]
