import pytest
from PIL import Image

from ascii_media.converter import ConverterOptions, image_to_ascii


def test_image_dimensions_are_corrected_for_terminal_cells() -> None:
    image = Image.new("RGB", (100, 50), "white")
    frame = image_to_ascii(image, ConverterOptions(width=20, char_aspect=0.5))

    assert len(frame.lines) == 5
    assert all(len(line) == 20 for line in frame.lines)
    assert len(frame.colors) == 5


def test_dark_and_light_pixels_map_to_charset_ends() -> None:
    image = Image.new("RGB", (2, 1))
    image.putdata([(0, 0, 0), (255, 255, 255)])
    frame = image_to_ascii(
        image,
        ConverterOptions(width=2, charset="@ ", contrast=1, saturation=1, char_aspect=1),
    )

    assert frame.plain == "@ "


def test_invert_swaps_luminance_mapping() -> None:
    image = Image.new("RGB", (1, 1), "black")
    frame = image_to_ascii(
        image,
        ConverterOptions(width=1, charset="@ ", invert=True, contrast=1, char_aspect=1),
    )

    assert frame.plain == " "


@pytest.mark.parametrize("kwargs", [{"width": 0}, {"charset": "x"}, {"char_aspect": 0}])
def test_invalid_options_raise(kwargs: dict) -> None:
    with pytest.raises(ValueError):
        ConverterOptions(**kwargs)
