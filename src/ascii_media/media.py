"""Load still images, animated images, and video frames."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from PIL import Image, ImageSequence, UnidentifiedImageError

from .converter import AsciiFrame, ConverterOptions, image_to_ascii

IMAGE_EXTENSIONS = {".bmp", ".gif", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp"}
VIDEO_EXTENSIONS = {".avi", ".m4v", ".mkv", ".mov", ".mp4", ".webm"}


class UnsupportedMediaError(ValueError):
    """Raised when an input cannot be decoded as supported media."""


def _sample_indices(total: int, limit: int) -> set[int]:
    if total <= limit:
        return set(range(total))
    if limit == 1:
        return {0}
    return {round(index * (total - 1) / (limit - 1)) for index in range(limit)}


def iter_image_frames(
    path: Path, options: ConverterOptions, max_frames: int
) -> Iterator[AsciiFrame]:
    try:
        with Image.open(path) as image:
            total = getattr(image, "n_frames", 1)
            selected = _sample_indices(total, max_frames)
            for index, frame in enumerate(ImageSequence.Iterator(image)):
                if index not in selected:
                    continue
                duration = max(0.02, float(frame.info.get("duration", 100)) / 1000)
                converted = image_to_ascii(frame.copy().convert("RGB"), options)
                yield AsciiFrame(converted.lines, converted.colors, duration)
    except (OSError, UnidentifiedImageError) as error:
        raise UnsupportedMediaError(f"Could not decode image: {path}") from error


def iter_video_frames(
    path: Path,
    options: ConverterOptions,
    max_frames: int,
    target_fps: float,
) -> Iterator[AsciiFrame]:
    try:
        import cv2  # type: ignore[import-not-found]
    except ImportError as error:
        raise UnsupportedMediaError(
            "Video support requires the optional dependency. "
            "Install with: pip install 'ascii-media[video]'"
        ) from error

    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        raise UnsupportedMediaError(f"Could not decode video: {path}")

    source_fps = capture.get(cv2.CAP_PROP_FPS) or target_fps
    total = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total / source_fps if total > 0 else max_frames / target_fps
    desired_count = min(max_frames, max(1, round(duration * target_fps)))
    frame_duration = duration / desired_count if total > 0 else 1 / target_fps
    selected = _sample_indices(total, desired_count) if total > 0 else set()
    fallback_step = max(1, round(source_fps / target_fps))
    emitted = 0
    frame_index = 0

    try:
        while emitted < max_frames:
            success, bgr_frame = capture.read()
            if not success:
                break
            should_emit = frame_index in selected if selected else frame_index % fallback_step == 0
            if should_emit:
                rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
                converted = image_to_ascii(Image.fromarray(rgb_frame), options)
                yield AsciiFrame(converted.lines, converted.colors, frame_duration)
                emitted += 1
            frame_index += 1
    finally:
        capture.release()


def load_frames(
    path: Path,
    options: ConverterOptions,
    *,
    max_frames: int = 120,
    fps: float = 12,
) -> list[AsciiFrame]:
    """Decode a media file and return sampled ASCII frames."""

    if max_frames < 1:
        raise ValueError("max_frames must be at least 1")
    if fps <= 0:
        raise ValueError("fps must be greater than 0")
    suffix = path.suffix.lower()
    if suffix in IMAGE_EXTENSIONS:
        frames = list(iter_image_frames(path, options, max_frames))
    elif suffix in VIDEO_EXTENSIONS:
        frames = list(iter_video_frames(path, options, max_frames, fps))
    else:
        raise UnsupportedMediaError(
            f"Unsupported file type '{suffix or '(none)'}'. "
            "Use an image, GIF, or common video format."
        )
    if not frames:
        raise UnsupportedMediaError(f"No frames could be read from: {path}")
    return frames
