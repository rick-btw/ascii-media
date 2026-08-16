"""Image-to-ASCII conversion primitives."""

from __future__ import annotations

from dataclasses import dataclass

from PIL import Image, ImageEnhance, ImageOps
from rich.color import Color
from rich.style import Style
from rich.text import Text

DEFAULT_CHARSET = "@%#*+=-:. "


@dataclass(frozen=True, slots=True)
class ConverterOptions:
    """Controls image preprocessing and ASCII rendering."""

    width: int = 80
    charset: str = DEFAULT_CHARSET
    contrast: float = 1.5
    brightness: float = 1.0
    saturation: float = 1.25
    invert: bool = False
    char_aspect: float = 0.5

    def __post_init__(self) -> None:
        if self.width < 1:
            raise ValueError("width must be at least 1")
        if len(self.charset) < 2:
            raise ValueError("charset must contain at least two characters")
        if self.contrast < 0 or self.brightness < 0 or self.saturation < 0:
            raise ValueError("contrast, brightness, and saturation cannot be negative")
        if not 0 < self.char_aspect <= 1:
            raise ValueError("char_aspect must be greater than 0 and at most 1")


@dataclass(frozen=True, slots=True)
class AsciiFrame:
    """One rendered ASCII frame and its per-character RGB values."""

    lines: tuple[str, ...]
    colors: tuple[tuple[tuple[int, int, int], ...], ...]
    duration: float = 0.1

    @property
    def plain(self) -> str:
        return "\n".join(self.lines)

    def to_rich(self, *, color: bool = True) -> Text:
        output = Text()
        for row_index, line in enumerate(self.lines):
            for column_index, character in enumerate(line):
                style = None
                if color:
                    red, green, blue = self.colors[row_index][column_index]
                    style = Style(color=Color.from_rgb(red, green, blue))
                output.append(character, style=style)
            if row_index < len(self.lines) - 1:
                output.append("\n")
        return output


def _fit_size(image: Image.Image, width: int, char_aspect: float) -> tuple[int, int]:
    source_width, source_height = image.size
    if source_width < 1 or source_height < 1:
        raise ValueError("image has invalid dimensions")
    height = max(1, round((source_height / source_width) * width * char_aspect))
    return width, height


def _pixels(image: Image.Image) -> list:
    """Return flat pixel data across supported Pillow versions."""

    if hasattr(image, "get_flattened_data"):
        return list(image.get_flattened_data())
    return list(image.getdata())  # pragma: no cover - Pillow < 12


def image_to_ascii(image: Image.Image, options: ConverterOptions) -> AsciiFrame:
    """Convert a Pillow image to an :class:`AsciiFrame`."""

    rgb = image.convert("RGB")
    rgb = ImageEnhance.Contrast(rgb).enhance(options.contrast)
    rgb = ImageEnhance.Brightness(rgb).enhance(options.brightness)
    rgb = ImageEnhance.Color(rgb).enhance(options.saturation)
    rgb = rgb.resize(_fit_size(rgb, options.width, options.char_aspect), Image.Resampling.LANCZOS)

    grayscale = ImageOps.grayscale(rgb)
    if options.invert:
        grayscale = ImageOps.invert(grayscale)

    chars = options.charset
    last_index = len(chars) - 1
    pixel_values = _pixels(grayscale)
    color_values = _pixels(rgb)
    output_lines: list[str] = []
    output_colors: list[tuple[tuple[int, int, int], ...]] = []

    for y in range(rgb.height):
        offset = y * rgb.width
        row_values = pixel_values[offset : offset + rgb.width]
        row_colors = color_values[offset : offset + rgb.width]
        output_lines.append("".join(chars[value * last_index // 255] for value in row_values))
        output_colors.append(tuple(row_colors))

    return AsciiFrame(tuple(output_lines), tuple(output_colors))
