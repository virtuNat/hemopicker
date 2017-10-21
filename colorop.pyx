import pygame as pg


def to_hsv(color):
    """Return hsv tuple of given color, rgb tuple, or hexcolor."""
    cdef double r, g, b
    cdef double minc, maxc, chroma, sat, hue
    if isinstance(color, pg.Color) or isinstance(color, tuple):
        # r, g, b values must be evaluated as ratios
        r, g, b = map(lambda x: float(x) / 255, color[:3])
    elif isinstance(color, int):
        # Parse 0xRRGGBB hex value as color
        b = float(color % 256) / 255
        g = float(color // 256 % 256) / 255
        r = float(color // 256 ** 2 % 256) / 255
    minc = min(r, g, b)
    maxc = max(r, g, b)
    chroma = maxc - minc
    # Saturation is zero if Value is also zero
    sat = chroma / maxc if maxc else 0.
    if not chroma:
        # Grayscale Colors
        hue = 0.
    elif maxc == r:
        # Magenta to Yellow
        hue = (g-b) / chroma % 6
    elif maxc == g:
        # Yellow to Cyan
        hue = (b-r) / chroma + 2
    elif maxc == b:
        # Cyan to Magenta
        hue = (r-g) / chroma + 4
    # Return hue represented in degrees
    return (hue * 60, sat, maxc)


def to_rgb(color):
    """Convert hsv tuple back to rgb color value."""
    cdef double hue, sat, val, chroma
    cdef int minc, midc, maxc
    if not (isinstance(color, tuple) or len(color) == 3):
        raise TypeError('invalid color format')
    hue, sat, val = color
    hue /= 60
    chroma = sat * val
    minc = int(round(255 * (val - chroma)))
    midc = int(round(255 * (chroma * (1 - abs(hue%2 - 1)) + (val - chroma))))
    maxc = int(round(255 * val))
    if 0 <= hue < 1:
        # Red to Yellow
        return pg.Color(maxc, midc, minc)
    elif 1 <= hue < 2:
        # Yellow to Green
        return pg.Color(midc, maxc, minc)
    elif 2 <= hue < 3:
        # Green to Cyan
        return pg.Color(minc, maxc, midc)
    elif 3 <= hue < 4:
        # Cyan to Blue
        return pg.Color(minc, midc, maxc)
    elif 4 <= hue < 5:
        # Blue to Magenta
        return pg.Color(midc, minc, maxc)
    elif 5 <= hue < 6:
        # Magenta to Red
        return pg.Color(maxc, minc, midc)
    else:
        # Invalid Values
        return pg.Color(0, 0, 0)
