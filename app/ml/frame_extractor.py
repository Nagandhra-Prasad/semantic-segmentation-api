from pathlib import Path

import cv2


def extract_video_frames(
    video_path: str,
    output_dir: Path,
    frame_interval: int = 5,
    max_frames: int = 30,
) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    capture = cv2.VideoCapture(video_path)
    if not capture.isOpened():
        raise ValueError("Could not open video file")

    saved: list[str] = []
    index = 0
    frame_number = 0

    while len(saved) < max_frames:
        ok, frame = capture.read()
        if not ok:
            break
        if frame_number % frame_interval == 0:
            out_path = output_dir / f"frame_{index:04d}.jpg"
            cv2.imwrite(str(out_path), frame)
            saved.append(str(out_path))
            index += 1
        frame_number += 1

    capture.release()
    if not saved:
        raise ValueError("No frames extracted from video")
    return saved
