#!usr/bin/env python

import random
import pygame as pg
from colorop import to_rgb, to_hsv
from boilerplate import load_image
from boilerplate import Appli, AppState, FreeSprite, TextSprite


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

    def __init__(self, pos):
        super().__init__(
            image=pg.Surface((40, 40)),
            pos=pos,
            size=(40, 40),
            presspos=(0, 0),
            clippos=(0, 0),
            )
        self.color = 0x000000

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if not isinstance(value, pg.Color):
            self._color = pg.Color(value)
        else:
            self._color = value
        self.image.fill(value)



class GenerateButton(Button):

    def __init__(self, pos):
        super().__init__(
            image=buttonsheet,
            pos=pos,
            size=(78, 30),
            presspos=(0, 186),
            clippos=(0, 156),
            )


class Generate6Button(Button):

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


class Gamzee(FreeSprite):
    """Gamzee Makara's display sprite. Does nothing."""

    def __init__(self, **kwargs):
        super().__init__(
            image=load_image('gamzee.png', colorkey=0x00FF00),
            **kwargs,
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
            pos=(365, 100),
            size=(buttsize, buttsize),
            )
        self.castebuttons = [
            ColorButton(
                pos=(
                    305 + buttgap*(
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
            ColorHistoryButton(pos=(250, buttgap + i*buttgap))
            for i in range(5)
            ]
        self.copybuttons = [
            CopyButton((40, 246 + i*40))
            for i in range(3)
            ]
        self.genbutton = GenerateButton((304, 205))
        self.gen6button = Generate6Button((387, 205))

        self._color = pg.Color(0x000000FF)
        self.hextext = TextSprite(
            font=self.font,
            text=self.colorhex(),
            aa=True,
            color=pg.Color(0xFFFFFFFF),
            pos=(84, 250),
            )
        self.rgbtext = TextSprite(
            font=self.font,
            text=self.colorrgb(),
            aa=True,
            color=pg.Color(0xFFFFFFFF),
            pos=(84, 290),
            )
        self.hsvtext = TextSprite(
            font=self.font,
            text=self.colorhsv(),
            aa=True,
            color=pg.Color(0xFFFFFFFF),
            pos=(84, 330),
            )

        self.base_hue = 0
        self.castebuttons[self.base_hue].active = True

    def colorhex(self):
        """Returns the panel's current color as a hexstring."""
        return 'HEX: #{:06x}'.format((self._color.r*256 + self._color.g)*256 + self._color.b)

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
        self.oldcolors[0].color = self._color
        self._color = value

    def swap_color(self, idx):
        """Swap the currently used color with the given history index."""
        self._color, self.oldcolors[idx].color = self.oldcolors[idx].color, self._color
        
    def _generate(self):
        """Randomly generate a blood color."""
        if not self.mutantbutton.active:
            hue = self.base_hue * 30
            # Lime and Olive do not lie on multiples of 30 degrees.
            if hue == 90:
                hue = 73
            elif hue == 120:
                hue = 82
            # Induce slight hue variation.
            hue += random.triangular(0., 5., 0.)
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

    def generate(self):
        """Allow the button to update state when generate is used."""
        self.genbutton.pressed = True
        self._generate()

    def generate_six(self):
        """Fills up the history bar with generated shades and tints."""
        self.gen6button.pressed = True
        for _ in range(6):
            self._generate()

    def set_caste(self, idx):
        """Set the current caste to genereate blood colors from."""
        self.castebuttons[self.base_hue].active = False
        self.castebuttons[idx].active = True
        self.castebuttons[idx].pressed = True
        self.base_hue = idx

    def toggle_mutant(self):
        """Toggles allowing potential mutant colors."""
        self.mutantbutton.active = not self.mutantbutton.active
        self.mutantbutton.pressed = True

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
        elif self.gen6button.pressed:
            self.gen6button.pressed = False
        elif self.mutantbutton.pressed:
            self.mutantbutton.pressed = False
        elif self.castebuttons[self.base_hue].pressed:
            self.castebuttons[self.base_hue].pressed = False
            if not self.castebuttons[self.base_hue].active:
                self.castebuttons[self.base_hue].active = True
        else:
            for button in self.copybuttons:
                button.pressed = False

    def isclicked(self, button, cursor):
        """Alias to collidepoint function of the button's rect."""
        return getattr(self, button).rect.collidepoint(cursor)

    def update(self):
        """Updates object states."""
        # Update display values.
        self.panel.image.fill(self._color)
        self.hextext.text = self.colorhex()
        self.rgbtext.text = self.colorrgb()
        self.hsvtext.text = self.colorhsv()

        for button in self.castebuttons:
            button.update()
        for button in self.copybuttons:
            button.update()
        self.mutantbutton.update()
        self.genbutton.update()
        self.gen6button.update()

    def draw(self, surf):
        """Draws all sprites."""
        self.panel.draw(surf)
        self.mutantbutton.draw(surf)
        for button in self.castebuttons:
            button.draw(surf)
        for button in self.oldcolors:
            button.draw(surf)
        for button in self.copybuttons:
            button.draw(surf)
        self.genbutton.draw(surf)
        self.gen6button.draw(surf)
        self.hextext.draw(surf)
        self.rgbtext.draw(surf)
        self.hsvtext.draw(surf)


class ColorMenu(AppState):
    """docstring"""

    CONFIG = {
        pg.K_SPACE: 'generate',
        pg.K_m: 'mutant',
        }

    def __init__(self):
        self.bg = pg.Surface(self.owner.rect.size)
        self.gamzee = Gamzee(topright=(self.owner.rect.topright))
        self.colorset = ColorSet()

    def eval_events(self):
        """Handles all event logic."""
        for event in next(self.events):
            if event.type == pg.KEYDOWN:
                try:
                    action = self.CONFIG[event.key]
                except KeyError:
                    continue
                if action == 'generate':
                    self.colorset.generate()
                    continue
                elif action == 'mutant':
                    self.colorset.toggle_mutant()
                    continue
            elif event.type == pg.KEYUP:
                try:
                    action = self.CONFIG[event.key]
                except KeyError:
                    continue
                self.colorset.unpress()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos = event.pos
                    if self.colorset.isclicked('genbutton', pos):
                        self.colorset.generate()
                        continue
                    elif self.colorset.isclicked('gen6button', pos):
                        self.colorset.generate_six()
                        continue
                    elif self.colorset.isclicked('mutantbutton', pos):
                        self.colorset.toggle_mutant()
                        continue
                    else:
                        # Turn cursor position into a rect to take advantage of Rect.collidelist
                        rpos = pg.Rect(pos, (1, 1))
                        idx = rpos.collidelist(self.colorset.castebuttons)
                        if idx >= 0:
                            # Switch caste hue
                            if self.colorset.castebuttons[idx].active:
                                self.colorset.castebuttons[idx].pressed = True
                                continue
                            self.colorset.set_caste(idx)
                            continue
                        idx = rpos.collidelist(self.colorset.oldcolors)
                        if idx >= 0:
                            # Look at previous colors
                            self.colorset.swap_color(idx)
                            continue
                        idx = rpos.collidelist(self.colorset.copybuttons)
                        if idx >= 0:
                            self.colorset.clip_color(idx)
                            continue
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    self.colorset.unpress()

    def eval_logic(self):
        """Handles logic not requiring event handling."""
        self.colorset.update()

    def display(self):
        """Handles the display."""
        drawsurf = self.window
        drawsurf.blit(self.bg, (0, 0))
        self.gamzee.draw(drawsurf)
        self.colorset.draw(drawsurf)
        pg.display.flip()


app.set_states(picker=ColorMenu)
app.run()
