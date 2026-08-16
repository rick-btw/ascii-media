"""Export ASCII frames as text, Markdown, or self-contained HTML."""

from __future__ import annotations

import html
import json
from pathlib import Path

from .converter import AsciiFrame


def _text_frames(frames: list[AsciiFrame]) -> str:
    return "\n\n--- frame ---\n\n".join(frame.plain for frame in frames) + "\n"


def export_text(frames: list[AsciiFrame], destination: Path) -> None:
    destination.write_text(_text_frames(frames), encoding="utf-8")


def export_markdown(frames: list[AsciiFrame], destination: Path, title: str) -> None:
    sections: list[str] = [f"# {title}", ""]
    for index, frame in enumerate(frames, start=1):
        if len(frames) > 1:
            sections.extend((f"## Frame {index}", ""))
        sections.extend(("```text", frame.plain, "```", ""))
    destination.write_text("\n".join(sections), encoding="utf-8")


def _html_frame(frame: AsciiFrame) -> str:
    rows: list[str] = []
    for line, colors in zip(frame.lines, frame.colors, strict=True):
        spans: list[str] = []
        active_color: tuple[int, int, int] | None = None
        active_text: list[str] = []
        for character, color in zip(line, colors, strict=True):
            if color != active_color and active_text:
                red, green, blue = active_color  # type: ignore[misc]
                spans.append(
                    f'<span style="color:rgb({red},{green},{blue})">'
                    f"{html.escape(''.join(active_text))}</span>"
                )
                active_text = []
            active_color = color
            active_text.append(character)
        if active_text and active_color is not None:
            red, green, blue = active_color
            spans.append(
                f'<span style="color:rgb({red},{green},{blue})">'
                f"{html.escape(''.join(active_text))}</span>"
            )
        rows.append("".join(spans))
    return "\n".join(rows)


def export_html(frames: list[AsciiFrame], destination: Path, title: str) -> None:
    rendered_frames = [_html_frame(frame) for frame in frames]
    durations = [round(frame.duration * 1000) for frame in frames]
    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{ color-scheme: dark; }}
    body {{ margin: 0; min-height: 100vh; display: grid; place-items: center;
      background: #080a0f; overflow: auto; }}
    pre {{ margin: 1rem; padding: 1.25rem; font: 700 10px/1 monospace;
      letter-spacing: 0; background: #0e1118; border: 1px solid #252a36;
      border-radius: .75rem; box-shadow: 0 1rem 3rem #0008; }}
  </style>
</head>
<body>
  <pre id="art" aria-label="{html.escape(title)}"></pre>
  <script>
    const frames = {json.dumps(rendered_frames)};
    const durations = {json.dumps(durations)};
    const art = document.getElementById("art");
    let index = 0;
    function draw() {{
      art.innerHTML = frames[index];
      const delay = durations[index];
      index = (index + 1) % frames.length;
      if (frames.length > 1) window.setTimeout(draw, delay);
    }}
    draw();
  </script>
</body>
</html>
"""
    destination.write_text(document, encoding="utf-8")


def export_frames(frames: list[AsciiFrame], destination: Path, title: str) -> None:
    """Choose an exporter based on the destination suffix."""

    suffix = destination.suffix.lower()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if suffix == ".txt":
        export_text(frames, destination)
    elif suffix in {".md", ".markdown"}:
        export_markdown(frames, destination, title)
    elif suffix in {".html", ".htm"}:
        export_html(frames, destination, title)
    else:
        raise ValueError("export path must end in .txt, .md, .markdown, .html, or .htm")

