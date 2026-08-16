from pathlib import Path

from PIL import Image

from ascii_media.cli import build_parser, run


def test_cli_exports_without_preview(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    destination = tmp_path / "out.txt"
    Image.new("RGB", (8, 8), "white").save(source)
    args = build_parser().parse_args([str(source), "-o", str(destination), "--export-only"])

    assert run(args) == 0
    assert destination.exists()


def test_cli_reports_missing_input(tmp_path: Path) -> None:
    args = build_parser().parse_args([str(tmp_path / "missing.png")])
    assert run(args) == 2

