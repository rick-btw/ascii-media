from pathlib import Path

import cv2
import numpy as np
import pytest
from PIL import Image

from ascii_media.converter import ConverterOptions
from ascii_media.media import UnsupportedMediaError, load_frames


def test_loads_a_still_image(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    Image.new("RGB", (10, 10), "#ff6600").save(source)

    frames = load_frames(source, ConverterOptions(width=8))

    assert len(frames) == 1
    assert len(frames[0].lines[0]) == 8


def test_samples_animated_gif(tmp_path: Path) -> None:
    source = tmp_path / "animated.gif"
    images = [Image.new("RGB", (4, 4), color) for color in ("red", "green", "blue")]
    images[0].save(source, save_all=True, append_images=images[1:], duration=50, loop=0)

    frames = load_frames(source, ConverterOptions(width=4), max_frames=2)

    assert len(frames) == 2


def test_loads_and_samples_a_video(tmp_path: Path) -> None:
    source = tmp_path / "clip.avi"
    writer = cv2.VideoWriter(
        str(source), cv2.VideoWriter_fourcc(*"MJPG"), 5, (16, 16)
    )
    assert writer.isOpened()
    for value in (0, 80, 160, 240):
        writer.write(np.full((16, 16, 3), value, dtype=np.uint8))
    writer.release()

    frames = load_frames(source, ConverterOptions(width=8), max_frames=2, fps=5)

    assert len(frames) == 2
    assert all(len(frame.lines[0]) == 8 for frame in frames)
    assert sum(frame.duration for frame in frames) == pytest.approx(0.8)


def test_rejects_unknown_media_type(tmp_path: Path) -> None:
    source = tmp_path / "source.xyz"
    source.write_text("not media")

    with pytest.raises(UnsupportedMediaError, match="Unsupported file type"):
        load_frames(source, ConverterOptions())
