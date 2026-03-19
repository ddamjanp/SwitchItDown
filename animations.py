import pygame as pg


def rc_to_indices(row1, col1, col2, cols, reverse=False):
    r0 = row1 - 1
    seq = [r0 * cols + (c - 1) for c in range(col1, col2 + 1)]
    return list(reversed(seq)) if reverse else seq


def slice_sheet(sheet: pg.Surface, fw: int, fh: int):
    """Safe slicer: uses integer rows/cols; never goes out of bounds."""
    frames = []
    sw, sh = sheet.get_size()
    cols, rows = sw // fw, sh // fh

    for r in range(rows):
        for c in range(cols):
            rect = pg.Rect(c * fw, r * fh, fw, fh)
            frames.append(sheet.subsurface(rect).copy().convert_alpha())

    return frames


def scale_to_h(surface: pg.Surface, h: int) -> pg.Surface:
    w, oh = surface.get_size()
    return pg.transform.smoothscale(surface, (int(w * h / oh), h))


class Animator:
    def __init__(self, frames, fps=8, loop=True):
        self.frames = frames[:]
        self.fps = max(1, fps)
        self.loop = loop
        self.i = 0
        self.t = 0.0
        self.done = False

    def reset(self):
        self.i = 0
        self.t = 0.0
        self.done = False

    def update(self, dt):
        if not self.frames or self.done:
            return

        self.t += dt
        dur = 1.0 / self.fps

        while self.t >= dur:
            self.t -= dur
            self.i += 1

            if self.i >= len(self.frames):
                if self.loop:
                    self.i = 0
                else:
                    self.i = len(self.frames) - 1
                    self.done = True
                    break

    def get(self):
        return self.frames[self.i] if self.frames else None

    def len(self):
        return len(self.frames)


def build_clip(frames, start, count, fps=8, loop=True):
    return Animator(frames[start:start + count], fps=fps, loop=loop)


def build_clip_by_indices(frames, indices, fps=10, loop=True):
    seq = [frames[i] for i in indices]
    return Animator(seq, fps=fps, loop=loop)


def blit_faced(surface, frame, pos, facing):
    if facing == -1:
        frame = pg.transform.flip(frame, True, False)
    surface.blit(frame, pos)


def clamp_draw_x(x, fw, width, margin=0):
    return max(margin, min(width - margin - fw, x))
