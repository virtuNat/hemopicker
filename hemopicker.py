#!/usr/bin/env python

import pygame as pg
from colorset import ColorSet, app
from boilerplate import load_image
from boilerplate import AppState, FreeSprite


class Gamzee(FreeSprite):
    """Gamzee Makara's display sprite. Does nothing."""

    def __init__(self, **kwargs):
        super().__init__(
            image=load_image('gamzee.png', colorkey=0x00FF00),
            **kwargs,
            )


class ColorMenu(AppState):
    """docstring"""

    def __init__(self):
        self.bg = pg.Surface(self.owner.rect.size)
        self.panel = load_image('panel.png', colorkey=0xFF00FF)
        self.gamzee = Gamzee(topright=(self.owner.rect.topright))
        self.colorset = ColorSet()

    def eval_events(self):
        """Handles all event logic."""
        for event in next(self.events):
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos = event.pos
                    if self.colorset.isclicked('genbutton', pos):
                        self.colorset.generate()
                        continue
                    elif self.colorset.isclicked('genallbutton', pos):
                        self.colorset.generate_all()
                        continue
                    elif self.colorset.isclicked('mutantbutton', pos):
                        self.colorset.toggle_mutant()
                        continue
                    elif self.colorset.isclicked('randombutton', pos):
                        self.colorset.toggle_random()
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
        self.colorset.draw(drawsurf)
        drawsurf.blit(self.panel, (0, 0))
        self.gamzee.draw(drawsurf)
        pg.display.flip()


app.set_states(picker=ColorMenu)
app.run()
