from pathlib import Path

import pytest

from ascii_media.converter import AsciiFrame
from ascii_media.exporters import export_frames


@pytest.fixture
def frame() -> AsciiFrame:
    return AsciiFrame(("<&",), (((255, 0, 0), (0, 255, 0)),), 0.1)


def test_text_export(tmp_path: Path, frame: AsciiFrame) -> None:
    destination = tmp_path / "art.txt"
    export_frames([frame], destination, "Test")
    assert destination.read_text() == "<&\n"


def test_markdown_export_is_fenced(tmp_path: Path, frame: AsciiFrame) -> None:
    destination = tmp_path / "art.md"
    export_frames([frame], destination, "Banner")
    content = destination.read_text()
    assert "# Banner" in content
    assert "```text\n<&\n```" in content


def test_html_export_escapes_content(tmp_path: Path, frame: AsciiFrame) -> None:
    destination = tmp_path / "art.html"
    export_frames([frame], destination, "Test")
    content = destination.read_text()
    assert "&lt;" in content
    assert "&amp;" in content
    assert "rgb(255,0,0)" in content
    assert "<!doctype html>" in content


def test_unknown_export_extension_fails(tmp_path: Path, frame: AsciiFrame) -> None:
    with pytest.raises(ValueError, match="export path"):
        export_frames([frame], tmp_path / "art.pdf", "Test")
