"""Command-line interface for ASCII Media."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.live import Live
from rich.panel import Panel

from . import __version__
from .converter import DEFAULT_CHARSET, AsciiFrame, ConverterOptions
from .exporters import export_frames
from .media import UnsupportedMediaError, load_frames

console = Console()
error_console = Console(stderr=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ascii-media",
        description="Convert images, GIFs, and short videos into colored terminal ASCII art.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("input", type=Path, help="image, GIF, or video file")
    parser.add_argument("-w", "--width", type=int, default=80, help="output width in characters")
    parser.add_argument("--charset", default=DEFAULT_CHARSET, help="characters from dark to light")
    parser.add_argument("--contrast", type=float, default=1.5, help="contrast multiplier")
    parser.add_argument("--brightness", type=float, default=1.0, help="brightness multiplier")
    parser.add_argument(
        "--saturation", type=float, default=1.25, help="color saturation multiplier"
    )
    parser.add_argument(
        "--invert", action="store_true", help="invert luminance-to-character mapping"
    )
    parser.add_argument("--no-color", action="store_true", help="disable terminal RGB colors")
    parser.add_argument(
        "--aspect", type=float, default=0.5, help="terminal character aspect correction"
    )
    parser.add_argument("--fps", type=float, default=12, help="target video playback FPS")
    parser.add_argument("--max-frames", type=int, default=120, help="maximum frames to decode")
    parser.add_argument("-o", "--output", type=Path, help="export to .txt, .md, or .html")
    parser.add_argument(
        "--export-only", action="store_true", help="write output without terminal preview"
    )
    parser.add_argument("--loop", action="store_true", help="loop animated preview until Ctrl+C")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def _preview(frames: list[AsciiFrame], color: bool, loop: bool) -> None:
    if len(frames) == 1:
        console.print(frames[0].to_rich(color=color))
        return

    try:
        with Live(console=console, refresh_per_second=30, transient=False) as live:
            while True:
                for frame in frames:
                    live.update(
                        Panel.fit(frame.to_rich(color=color), border_style="dim"), refresh=True
                    )
                    time.sleep(frame.duration)
                if not loop:
                    break
    except KeyboardInterrupt:
        pass


def run(args: argparse.Namespace) -> int:
    input_path: Path = args.input.expanduser()
    if not input_path.is_file():
        error_console.print(f"[bold red]Error:[/] input file does not exist: {input_path}")
        return 2
    if args.export_only and not args.output:
        error_console.print("[bold red]Error:[/] --export-only requires --output")
        return 2

    try:
        options = ConverterOptions(
            width=args.width,
            charset=args.charset,
            contrast=args.contrast,
            brightness=args.brightness,
            saturation=args.saturation,
            invert=args.invert,
            char_aspect=args.aspect,
        )
        with console.status("[bold cyan]Converting media…"):
            frames = load_frames(
                input_path, options, max_frames=args.max_frames, fps=args.fps
            )
        if args.output:
            destination: Path = args.output.expanduser()
            export_frames(frames, destination, input_path.stem)
            console.print(f"[green]Exported[/] {len(frames)} frame(s) to {destination}")
        if not args.export_only:
            _preview(frames, color=not args.no_color, loop=args.loop)
    except (UnsupportedMediaError, ValueError, OSError) as error:
        error_console.print(f"[bold red]Error:[/] {error}")
        return 2
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    arguments = parser.parse_args(argv)
    raise SystemExit(run(arguments))


if __name__ == "__main__":
    main(sys.argv[1:])
