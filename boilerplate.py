import os
import sys
import asyncio

from math import cos, sin, radians, hypot
from functools import partialmethod
from traceback import print_exception

import pygame as pg
pg.init()


def dcos(angle):
    """Degree cosine."""
    return cos(radians(angle))


def dsin(angle):
    """Degree sine."""
    return sin(radians(angle))


def get_dist(p1, p2):
    """Get Euclidean distance between two points as tuples."""
    return hypot(p1[0] - p2[0], p1[1] - p2[1])


def get_cos(p1, p2):
    """Get cosine from point 1 to 2."""
    return (p2[0]-p1[0]) / hypot(p1[0] - p2[0], p1[1] - p2[1])


def get_sin(p1, p2):
    """Get sine from point 1 to 2."""
    return (p2[1]-p1[1]) / hypot(p1[0] - p2[0], p1[1] - p2[1])


def load_image (name, alpha=None, colorkey=None):
    """Load an image file into memory. Try not to keep too many of these in memory."""
    try:
        image = pg.image.load(os.path.join('textures', name))
    except pg.error:
        print('Image loading failed: ')
        raise
    if alpha is None:
        image = image.convert()
        if colorkey is not None:
            image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def _dict_setter(obj, in_dict=None, name='dict', **dargs):
    """Used to set application state and key configurations."""
    if in_dict or isinstance(in_dict, dict):
        if isinstance(in_dict, dict):
            setattr(obj, name, in_dict)
        else:
            raise TypeError(
                'Expected dictionary, got {}.'.format(
                    dicts[0].__class__.__name__
                    )
                )
    elif len(dargs) > 0:
        setattr(obj, name, dargs)
    else:
        print(in_dict, name, dargs)
        raise TypeError('None is not a dict instance')


class AppExit(BaseException):
    """Raised when the user wants to exit safely."""


class FreeSprite(pg.sprite.Sprite):
    """Object that handles basic Sprite functions."""

    def __init__(self, image, **kwargs):
        super().__init__()
        self.image = image
        self.rect = kwargs.pop(
            'rect',
            pg.Rect(
                kwargs.pop('pos', (0, 0)),
                kwargs.pop('size', self.image.get_size())),
            )
        self.cliprect = kwargs.pop(
            'cliprect',
            pg.Rect(
                kwargs.pop('clippos', (0, 0)),
                kwargs.pop('clipsize', self.rect.size),
                )
            )
        self.set(**kwargs)
        self.pos = map(float, self.rect.center)

    def set(self, **anchors):
        """Sets an anchor for the sprite's rect."""
        for name, value in anchors.items():
            if value == 'pos':
                value = self.pos
            setattr(self.rect, name, value)

    def move_xy (self, dx, dy, **anchors):
        """Move sprite a given distance relative to pixel grid."""
        # Add the offset.
        self.pos = self.pos[0] + dx, self.pos[1] + dy
        # Anchor to center of image rectangle by default.
        self.set(**anchors if anchors else {'center': 'pos'})

    def move_rt (self, dist, angle, **anchors):
        """Move sprite a given distance in a given direction."""
        # Convert to rectangular coordinates and add the offset.
        self.pos = (self.pos[0] + dist*dcos(angle),
                    self.pos[1] + dist*dsin(angle)
                    )
        # Anchor to center of image rectangle by default.
        self.set(**anchors if anchors else {'center': 'pos'})

    def move_to (self, dest, dist, **anchor):
        """Move sprite towards a destination a given distance."""
        # If the destination is closer than the distance, 
        # set position to destination.
        if get_dist(self.pos, dest) > dist:
            self.pos = (self.pos[0] + dist*get_cos(self.pos, dest),
                        self.pos[1] + dist*get_sin(self.pos, dest)
                        )
        else:
            self.pos = dest
        # Anchor to center of image rectangle by default.
        self.set(**anchors if anchors else {'center': 'pos'})

    def update(self):
        """Ideally called once per frame. Override this."""
        raise NotImplementedError('update method must be overridden')

    def draw(self, target):
        """Draw this sprite on a target surface or sprite."""
        if isinstance(target, pg.Surface):
            target.blit(self.image, self.rect, self.cliprect)
        else:
            try:
                target.image.blit(self.image, self.rect, self.cliprect)
            except AttributeError:
                raise AttributeError(
                    'target must be Surface or have image attribute'
                    )


class TextSprite(FreeSprite):
    """Object class to handle text rendering as a sprite."""

    def __init__(self, **kwargs):
        self.font = kwargs.pop(
            'font',
            pg.font.Font(
                kwargs.pop('fontname', None),
                kwargs.pop('fontsize', 25),
                ),
            )
        self._text = kwargs.pop('text', '')
        self.aa = kwargs.pop('aa', 0)
        self._color = kwargs.pop('color', pg.Color(0x000000FF))
        self.bg = kwargs.pop('background', None)
        super().__init__(
            image=self.font.render(self._text, self.aa, self._color, self.bg),
            size=self.font.size(self._text),
            **kwargs,
            )

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, newtext):
        self._text = newtext
        self.image = self.font.render(newtext, self.aa, self._color, self.bg)
        self.set(size=self.image.get_size())
        self.cliprect.size = self.rect.size

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, newcolor):
        self._color = newcolor
        self.image = self.font.render(self._text, self.aa, newcolor, self.bg)

    def render(self):
        return self.font.render(self._text, self.aa, newcolor, self.bg)


class State:
    """Base Class for State classes. Used for type comparisons."""
    CONFIG = {pg.K_RETURN: 'accept', pg.K_ESCAPE: 'cancel'}
    set_config = partialmethod(_dict_setter, name='CONFIG')
    font = pg.font.SysFont('courier', 25)

    def display(self):
        """Dummy display function. Override this."""
        raise NotImplementedError('Override display handler when subclassing.')

    def eval_exit(self):
        """Handle safely exiting the program. Override this."""
        raise AppExit


class AppState(State):
    """Top-level object handler template for use as states in the application."""

    def eval_events(self):
        """Dummy event function. Override this."""
        
        # Sample usage:
        for event in pg.event.get():
            if event.type is pg.QUIT:
                raise AppExit
            elif event.type is pg.KEYDOWN:
                try:
                    action = self.CONFIG[event.key]
                except KeyError:
                    continue
                # Evaluate actions...

    def eval_logic(self):
        """Dummy logic function. Override this."""
        raise NotImplementedError('Override logic handler when subclassing.')

    def run(self):
        """Called by Appli.run to manage the internal code."""
        try:
            self.eval_events()
            self.eval_logic()
        except AppExit:
            self.eval_exit()
        self.display()


class AsyncState(State):
    """Async version of the AppState top-level handler template."""

    async def eval_events(self):
        """Dummy event function. Override this."""
        
        # Sample usage:
        for event in pg.event.get():
            if event.type is pg.QUIT:
                raise AppExit
            elif event.type is pg.KEYDOWN:
                try:
                    action = self.CONFIG[event.key]
                except KeyError:
                    continue
                # Evaluate actions...

    async def eval_logic(self):
        """Dummy logic function. Override this."""
        raise NotImplementedError('Override logic handler when subclassing.')

    async def run(self):
        """Called by Appli.run to manage the internal code."""
        try:
            await self.eval_events()
            await self.eval_logic()
        except AppExit:
            self.eval_exit()
        # Display must always be last.
        self.display()


class Window:
    """Represents the display surface."""

    def __init__(self, **kwargs):
        pg.display.set_caption(
            kwargs.get('name', 'pygame window')
            )
        self.flags = kwargs.get('flags', 0)
        self.surf = kwargs.get(
            'surf',
            pg.display.set_mode(
                kwargs.get('size', (200, 200)),
                self.flags,
                )
            )
        self.rect = self.surf.get_rect()

    def set_size(self, size):
        self.surf = pg.display.set_mode(size, self.flags)

    def resize(self, newsize):
        if self.flags & pg.RESIZABLE:
            self.surf = pg.display.set_mode(newsize, self.flags)
            self.rect = self.surf.get_rect()
        else:
            raise ValueError('Can\'t resize unresizable window.')


class Appli:
    """Meta-handler of the program."""

    loop = asyncio.get_event_loop()
    _STATES = {'game': None} 

    def __init__(self, **kwargs):
        # Application window.
        try:
            self.window = kwargs['window']
        except KeyError:
            self.window = Window()
        # Application state system.
        self.set_states(kwargs.get('state_list', {}))
        self._state = kwargs.get('state', 'game')
        # Application display framerate.
        self.clock = kwargs.get('clock', pg.time.Clock())
        self.fps_cap = kwargs.get('fps_cap', 30)

        self.exit_status = 0
        self.do_async = False

    def __getattr__(self, name):
        """Define getter descriptors."""
        if name == 'state':
            try:
                return self._STATES[self._state]
            except KeyError:
                raise NameError(
                    'application state <{}> is not defined'.format(self._state)
                    )
        elif name == 'STATES':
            return self._STATES

    def __setattr__(self, name, value):
        """Define setter descriptors."""
        if name == 'state':
            self._state = value
        elif name == 'STATES' and value:
            for key, item in value.items():
                item.owner = self
                item.window = self.window
                self._STATES[key] = item()
        else:
            super().__setattr__(name, value)

    set_states = partialmethod(_dict_setter, name='STATES')

    def run(self):
        """Looping run code that allows for error handling."""
        try:
            if self.do_async:
                while True:
                    self.loop.run_until_complete(
                        self.state.run()
                        )
                    self.clock.tick(self.fps_cap)
            else:
                while True:
                    self.state.run()
                    self.clock.tick(self.fps_cap)
        except Exception:
            # Stupid catch-all exception so exit_status can be modified.
            self.exit_status = 1
            print_exception(*sys.exc_info(), file=sys.stdout)
            raise
        finally:
            # Ensure that the exit method is always executed.
            self.exit()

    def exit(self):
        """Exit the program once the finally clause is reached,
        or the user closes the window.
        """
        self.loop.close()
        pg.quit()
        sys.exit(self.exit_status)

Window()
