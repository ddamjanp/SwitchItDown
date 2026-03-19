import pygame as pg

from settings import WIN_W
from animations import Animator


class Fireball:
    def __init__(self, frames, x, y, vx):
        self.anim = Animator(frames, fps=16, loop=True)
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.alive = True

    def update(self, dt):
        self.anim.update(dt)
        self.x += self.vx * dt
        if self.x < -200 or self.x > WIN_W + 200:
            self.alive = False

    def frame(self):
        return self.anim.get()

    def rect(self):
        fr = self.frame()
        if not fr:
            return pg.Rect(int(self.x), int(self.y), 0, 0)
        w, h = fr.get_size()
        return pg.Rect(int(self.x), int(self.y), w, h)

    def draw(self, screen):
        fr = self.frame()
        if not fr:
            return
        if self.vx < 0:
            fr = pg.transform.flip(fr, True, False)
        screen.blit(fr, (int(self.x), int(self.y)))