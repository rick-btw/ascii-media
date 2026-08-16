# ASCII Media

Turn images, animated GIFs, and short video clips into crisp, high-contrast, true-color ASCII art—
directly in your terminal or exported as a shareable text, Markdown, or HTML banner.

<p align="center">
  <strong>Fast terminal previews · 24-bit color · Animated media · Zero-config image support</strong>
</p>

## Features

- Converts PNG, JPEG, WebP, TIFF, BMP, and animated GIF files with Pillow
- Plays sampled MP4, MOV, WebM, MKV, AVI, and M4V clips in the terminal
- Preserves source colors with Rich true-color rendering
- Tunes width, contrast, brightness, saturation, character ramp, and aspect ratio
- Exports plain `.txt`, fenced Markdown banners, or self-contained colored HTML
- Produces animated HTML when the source contains multiple frames
- Works as both an installed command and `python -m ascii_media`

## Installation

ASCII Media requires Python 3.10 or newer.

```bash
git clone https://github.com/<your-username>/ascii-media.git
cd ascii-media
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e .
```

For video support, install the optional OpenCV dependency:

```bash
python -m pip install -e ".[video]"
```

## Quick start

Preview an image in the terminal:

```bash
ascii-media photo.jpg
```

Increase detail and contrast:

```bash
ascii-media photo.jpg --width 120 --contrast 1.8 --saturation 1.4
```

Play a short video at 15 sampled frames per second:

```bash
ascii-media clip.mp4 --width 90 --fps 15 --max-frames 180
```

Export a colored, self-contained HTML banner:

```bash
ascii-media logo.png --width 100 --output exports/logo.html --export-only
```

Export formats are selected by the file extension:

```bash
ascii-media image.png -o banner.txt
ascii-media image.png -o banner.md
ascii-media animation.gif -o animation.html
```

## Options

| Option | Purpose | Default |
| --- | --- | ---: |
| `-w`, `--width` | Output width in terminal characters | `80` |
| `--charset` | Characters ordered from darkest to lightest | `@%#*+=-:. ` |
| `--contrast` | Contrast multiplier | `1.5` |
| `--brightness` | Brightness multiplier | `1.0` |
| `--saturation` | Color saturation multiplier | `1.25` |
| `--invert` | Reverse luminance mapping | off |
| `--no-color` | Render the terminal preview without RGB color | off |
| `--aspect` | Character-cell aspect correction | `0.5` |
| `--fps` | Target video sampling/playback rate | `12` |
| `--max-frames` | Maximum decoded frames | `120` |
| `-o`, `--output` | Export path (`.txt`, `.md`, or `.html`) | none |
| `--export-only` | Skip terminal preview | off |
| `--loop` | Repeat animated previews until `Ctrl+C` | off |

Run `ascii-media --help` for the complete command reference.

## How conversion works

Each source frame is resized to the requested terminal width with character-cell aspect correction.
Pillow applies contrast, brightness, and saturation adjustments, then maps pixel luminance to a
configurable character ramp. Rich applies each resized pixel's RGB value to the matching character.
Video frames are sampled with OpenCV so terminal playback remains responsive and bounded by
`--max-frames`.

## Tips

- Use a width close to your terminal's column count to avoid wrapping.
- Try `--invert` when rendering on a light terminal background.
- Shorter character ramps such as `"@#. "` look bolder; longer ramps retain more tonal detail.
- HTML exports preserve color and animate multi-frame inputs without external assets.
- Keep video previews short. Large widths and high frame counts consume substantially more memory.

## Development

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest
```

The GitHub Actions workflow runs linting and tests on Python 3.10 through 3.13. See
[CONTRIBUTING.md](CONTRIBUTING.md) before submitting a pull request.

## License

Released under the [MIT License](LICENSE).
