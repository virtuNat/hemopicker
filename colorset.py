"""Contains Sprites that control and display the blood colors to the user."""

import random
import pygame as pg

from colorop import to_rgb, to_hsv
from boilerplate import load_image
from boilerplate import Appli, FreeSprite, TextSprite

app = Appli(
    name='Fantroll Hemopicker',
    size=(800, 600),
    flags=pg.HWSURFACE,
    state='picker'
    )
buttonsheet = load_image('buttons.png', colorkey=0xFF00FF)

pg.scrap.init()


class Button(FreeSprite):
    """Button base sprite class."""

    def __init__(self, **kwargs):
        self.presspos = kwargs.pop('presspos', None)
        super().__init__(**kwargs)
        self.unpresspos = self.cliprect.topleft
        self.pressed = False

    def update(self):
        if self.pressed:
            self.cliprect.topleft = self.presspos
        else:
            self.cliprect.topleft = self.unpresspos


class ColorButton(Button):

    def __init__(self, **kwargs):
        super().__init__(
            image=buttonsheet,
            **kwargs,
            )
        self.active = False

    def update(self):
        self.cliprect.top = self.rect.h * (self.active*2 + self.pressed)


class ColorHistoryButton(Button):

    src = buttonsheet
    def __init__(self, pos):
        super().__init__(
            image=pg.Surface((40, 40)),
            pos=pos,
            size=(40, 40),
            presspos=(194, 196),
            clippos=(194, 156),
            )
        self.colorsurf = pg.Surface(self.rect.size)
        self.color = 0x000000
        self.hue = 0

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if not isinstance(value, pg.Color):
            self._color = pg.Color(value)
        else:
            self._color = value
        self.colorsurf.fill(value)

    def draw(self, surf):
        self.image.blit(self.colorsurf, (0, 0))
        self.image.blit(self.src, (0, 0), self.cliprect)
        surf.blit(self.image, self.rect)


class GenerateButton(Button):

    def __init__(self, pos):
        super().__init__(
            image=buttonsheet,
            pos=pos,
            size=(78, 30),
            presspos=(0, 186),
            clippos=(0, 156),
            )


class GenerateAllButton(Button):

    def __init__(self, pos):
        super().__init__(
            image=buttonsheet,
            pos=pos,
            size=(78, 30),
            presspos=(78, 186),
            clippos=(78, 156),
            )
        

class CopyButton(Button):

    def __init__(self, pos):
        super().__init__(
            image=buttonsheet,
            pos=pos,
            size=(38, 38),
            presspos=(156, 194),
            clippos=(156, 156),
            )


class ColorSet:

    COLORS = [ # Hemospectrum Reference
        pg.Color(0xA10000FF), # Burgundy
        pg.Color(0xA15203FF), # Bronze
        pg.Color(0xA1A100FF), # Ochre
        pg.Color(0x658200FF), # Lime
        pg.Color(0x416600FF), # Olive
        pg.Color(0x078446FF), # Jade
        pg.Color(0x008282FF), # Aqua
        pg.Color(0x004182FF), # Cobalt
        pg.Color(0x0041CBFF), # Indigo
        pg.Color(0x631DB4FF), # Purple
        pg.Color(0x6A006AFF), # Violet
        pg.Color(0x99004DFF), # Fuchsia
        ]

    def __init__(self):
        buttsize = 39
        buttgap = 40

        self.font = pg.font.SysFont('couriernew', 25)
        self.panel = FreeSprite(
            pg.Surface((200, 200)),
            pos=(40, 40),
            size=(200, 200),
            )
        self.mutantbutton = ColorButton(
            pos=(465, 245),
            size=(buttsize, buttsize),
            )
        self.randombutton = ColorButton(
            pos=(405, 100),
            size=(buttsize, buttsize),
            clippos=(507, 0),
            )
        self.castebuttons = [
            ColorButton(
                pos=(
                    345 + buttgap*(
                        3 if 3 < i < 8
                        else 2 if i == 3 or i == 8
                        else 1 if i == 2 or i == 9
                        else 0
                        ),
                    40 + buttgap*(
                        0 if 6 < i < 11
                        else 1 if i == 11 or i == 6
                        else 2 if i == 0 or i == 5
                        else 3
                        ),
                    ),
                size=(buttsize, buttsize),
                clippos=(buttsize * (i+1), 0),
                )
            for i in range(12)
            ]
        self.oldcolors = [
            ColorHistoryButton(pos=(250 + 45*(i//5), 40 + buttgap*(i%5)))
            for i in range(10)
            ]
        self.copybuttons = [
            CopyButton((40, 246 + i*buttgap))
            for i in range(3)
            ]
        self.genbutton = GenerateButton((344, 205))
        self.genallbutton = GenerateAllButton((427, 205))

        self._color = pg.Color(0x000000FF)
        self.hextext = TextSprite(
            font=self.font,
            text=self.colorhex(),
            aa=True,
            color=pg.Color(0xFFFFFFFF),
            pos=(90, 251),
            )
        self.rgbtext = TextSprite(
            font=self.font,
            text=self.colorrgb(),
            aa=True,
            color=pg.Color(0xFFFFFFFF),
            pos=(90, 291),
            )
        self.hsvtext = TextSprite(
            font=self.font,
            text=self.colorhsv(),
            aa=True,
            color=pg.Color(0xFFFFFFFF),
            pos=(90, 331),
            )

        self.base_hue = 0
        self.panel.hue = self.base_hue
        self.castebuttons[self.base_hue].active = True

    def colorhex(self):
        """Returns the panel's current color as a hexstring."""
        hexcolor = (self._color.r*256 + self._color.g)*256 + self._color.b
        return 'HEX: #{:06x}'.format(hexcolor).upper()

    def colorrgb(self):
        """Returns the panel's current color as a string."""
        return 'RGB: {color.r:03d}, {color.g:03d}, {color.b:03d}'.format(color=self._color)

    def colorhsv(self):
        """Returns the panel's current hsv color as a string."""
        return 'HSV: {:05.1f}°, {:04.2f}, {:04.2f}'.format(*to_hsv(self._color))

    @property
    def color(self):
        """The panel's current color value."""
        return self._color

    @color.setter
    def color(self, value):
        """Update panel and history when color is assigned to."""
        for i in range(len(self.oldcolors) - 1, 0, -1):
            self.oldcolors[i].color = self.oldcolors[i - 1].color
            self.oldcolors[i].hue = self.oldcolors[i - 1].hue
        self.oldcolors[0].color = self._color
        self.oldcolors[0].hue = self.panel.hue
        self._color = value
        self.panel.hue = self.base_hue

    def swap_color(self, idx):
        """Swap the currently used color with the given history index."""
        self.oldcolors[idx].pressed = True
        self._color, self.oldcolors[idx].color = self.oldcolors[idx].color, self._color
        self.castebuttons[self.base_hue].active = False
        self.panel.hue, self.oldcolors[idx].hue = self.oldcolors[idx].hue, self.panel.hue
        self.base_hue = self.panel.hue
        self.castebuttons[self.base_hue].active = True
        
    def _generate(self):
        """Randomly generate a blood color."""
        if self.randombutton.active:
            # The last hue used is valid only when the caste buttons haven't been pressed.
            self.castebuttons[self.base_hue].active = False
            self.base_hue = random.randrange(12)
            self.castebuttons[self.base_hue].active = True
        if not self.mutantbutton.active:
            hue = self.base_hue * 30
            # Lime and Olive do not lie on multiples of 30 degrees.
            if hue == 90:
                hue = 73
            elif hue == 120:
                hue = 82
            # Induce slight hue variation.
            hue += random.triangular(0., 7.5, 0.)
            sat = random.triangular(0.8, 1.0, 0.98)
            val = random.triangular(0.4, 0.8, 0.57)
        else:
            # Throw them a random color.
            hue = self.base_hue * 30 + random.uniform(-15., 15.)
            if hue < 0:
                hue += 360
            sat = random.random()
            val = random.random()
        self.color = to_rgb((hue, sat, val))
        self.generated = True

    def generate(self):
        """Allow the button to update state when generate is used."""
        self.genbutton.pressed = True
        self._generate()

    def generate_all(self):
        """Fills up the history bar with generated shades and tints."""
        self.pressed = True
        self.genallbutton.pressed = True
        for _ in range(11):
            self._generate()

    def set_caste(self, idx):
        """Set the current caste to genereate blood colors from."""
        self.castebuttons[idx].active = True
        self.castebuttons[idx].pressed = True
        self.castebuttons[self.base_hue].active = False
        # Last command was a caste set, generated is False.
        self.generated = False
        # Set new caste hue.
        self.base_hue = idx

    def toggle_mutant(self):
        """Toggles allowing potential mutant colors."""
        self.mutantbutton.active = not self.mutantbutton.active
        self.mutantbutton.pressed = True

    def toggle_random(self):
        """Toggles randomizing of blood caste."""
        self.randombutton.active = not self.randombutton.active
        self.randombutton.pressed = True

    def clip_color(self, idx):
        """Copy color data to clipboard."""
        self.copybuttons[idx].pressed = True
        if idx == 0:
            pg.scrap.put(
                pg.SCRAP_TEXT,
                self.colorhex()[5:].encode()
                )
        elif idx == 1:
            pg.scrap.put(
                pg.SCRAP_TEXT,
                '{rgb.r}, {rgb.g}, {rgb.b}'.format(
                    rgb=self._color
                    ).encode()
                )
        elif idx == 2:
            pg.scrap.put(
                pg.SCRAP_TEXT,
                '{hsv[0]:.1f}, {hsv[1]:.2f}, {hsv[2]:.2f}'.format(
                    hsv=to_hsv(self._color)
                    ).encode()
                )

    def unpress(self):
        """Resets pressed buttons."""
        if self.genbutton.pressed:
            self.genbutton.pressed = False
        elif self.genallbutton.pressed:
            self.genallbutton.pressed = False
        elif self.mutantbutton.pressed:
            self.mutantbutton.pressed = False
        elif self.randombutton.pressed:
            self.randombutton.pressed = False
        elif self.castebuttons[self.base_hue].pressed:
            self.castebuttons[self.base_hue].pressed = False
            # if not self.castebuttons[self.base_hue].active:
                # self.castebuttons[self.base_hue].active = True
        else:
            for button in self.copybuttons:
                button.pressed = False
            for button in self.oldcolors:
                button.pressed = False

    def isclicked(self, button, cursor):
        """Alias to collidepoint function of the button's rect."""
        return getattr(self, button).rect.collidepoint(cursor)

    def update(self):
        """Updates object states."""
        # Update display value.
        self.panel.image.fill(self._color)
        self.hextext.text = self.colorhex()
        self.rgbtext.text = self.colorrgb()
        self.hsvtext.text = self.colorhsv()
        # Update buttons.
        for button in self.castebuttons:
            button.update()
        for button in self.oldcolors:
            button.update()
        for button in self.copybuttons:
            button.update()
        self.mutantbutton.update()
        self.randombutton.update()
        self.genbutton.update()
        self.genallbutton.update()

    def draw(self, surf):
        """Draws all sprites."""
        self.panel.draw(surf)
        for button in self.castebuttons:
            button.draw(surf)
        for button in self.oldcolors:
            button.draw(surf)
        for button in self.copybuttons:
            button.draw(surf)
        self.mutantbutton.draw(surf)
        self.randombutton.draw(surf)
        self.genbutton.draw(surf)
        self.genallbutton.draw(surf)
        self.hextext.draw(surf)
        self.rgbtext.draw(surf)
        self.hsvtext.draw(surf)
