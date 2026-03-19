import pygame as pg

from settings import *
from animations import (
    slice_sheet,
    scale_to_h,
    build_clip,
    build_clip_by_indices,
)


def load_environment():
    sky = pg.transform.scale(pg.image.load(SKY_PATH).convert(), (WIN_W, WIN_H))
    sun = pg.transform.smoothscale(pg.image.load(SUN_PATH).convert_alpha(), (500, 500))
    block = pg.image.load(BLOCK_PATH).convert_alpha()

    return sky, sun, block


def load_fighter_frames():
    frames1 = [
        scale_to_h(f, TARGET_CHAR_H)
        for f in slice_sheet(pg.image.load(P1_SHEET).convert_alpha(), FRAME_W, FRAME_H)
    ]
    frames2 = [
        scale_to_h(f, TARGET_CHAR_H)
        for f in slice_sheet(pg.image.load(P2_SHEET).convert_alpha(), FRAME_W, FRAME_H)
    ]

    return frames1, frames2


def build_fighter_clips(frames):
    idle = build_clip(frames, IDLE_START_INDEX, IDLE_FRAME_COUNT, fps=8, loop=True)
    walk = build_clip(frames, WALK_START_INDEX, WALK_FRAME_COUNT, fps=8, loop=True)
    punch = build_clip_by_indices(frames, PUNCH_IDX, fps=12, loop=False)
    kick = build_clip_by_indices(frames, KICK_IDX, fps=12, loop=False)
    block = build_clip_by_indices(frames, BLOCK_IDX, fps=6, loop=True)
    combo = build_clip_by_indices(frames, COMBO_IDX, fps=14, loop=False)
    hit = build_clip_by_indices(frames, HIT_IDX, fps=12, loop=False)

    return idle, walk, punch, kick, block, combo, hit


def load_ghost_clips():
    ghost_surface = pg.image.load(GHOST_SHEET).convert_alpha()
    ghost_frames_raw = slice_sheet(ghost_surface, GHOST_FRAME_W, GHOST_FRAME_H)
    ghost_frames = [scale_to_h(f, TARGET_CHAR_H) for f in ghost_frames_raw]

    ghost_cols = ghost_surface.get_width() // GHOST_FRAME_W

    def gidx(r, c):
        return (r - 1) * ghost_cols + (c - 1)

    GHOST_TRANSFORM_IDX = [gidx(3, 5), gidx(1, 1)]
    GHOST_IDLE_IDX = [gidx(1, c) for c in range(1, 6)]
    GHOST_ATK_IDX = [gidx(2, c) for c in range(1, 6)]

    transform = build_clip_by_indices(ghost_frames, GHOST_TRANSFORM_IDX, fps=10, loop=False)
    idle = build_clip_by_indices(ghost_frames, GHOST_IDLE_IDX, fps=8, loop=True)
    attack = build_clip_by_indices(ghost_frames, GHOST_ATK_IDX, fps=10, loop=False)

    return idle, transform, attack


def load_beast_clips_p1():
    surface = pg.image.load(BEAST_SHEET).convert_alpha()
    frames_raw = slice_sheet(surface, BEAST_FRAME_W, BEAST_FRAME_H)
    frames = [scale_to_h(f, TARGET_CHAR_H) for f in frames_raw]

    cols = surface.get_width() // BEAST_FRAME_W

    def idx(r, c):
        return (r - 1) * cols + (c - 1)

    transform = build_clip_by_indices(frames, [idx(4, 5), idx(1, 1)], fps=10, loop=False)
    idle = build_clip_by_indices(frames, [idx(1, c) for c in range(1, 5)], fps=8, loop=True)
    walk = build_clip_by_indices(frames, [idx(2, c) for c in range(1, 5)], fps=8, loop=True)
    atk = build_clip_by_indices(frames, [idx(3, c) for c in range(1, 6)], fps=12, loop=False)
    sp = build_clip_by_indices(frames, [idx(3, c) for c in range(1, 7)], fps=12, loop=False)
    i_move = build_clip_by_indices(frames, [idx(6, c) for c in range(1, cols + 1)], fps=12, loop=False)
    hit = build_clip_by_indices(frames, [idx(4, c) for c in range(1, 5)], fps=12, loop=False)

    return idle, walk, transform, atk, sp, i_move, hit


def load_beast_clips_p2():
    surface = pg.image.load(P2_BEAST_SHEET).convert_alpha()
    frames_raw = slice_sheet(surface, BEAST_FRAME_W, BEAST_FRAME_H)
    frames = [scale_to_h(f, TARGET_CHAR_H) for f in frames_raw]

    cols = surface.get_width() // BEAST_FRAME_W

    def idx(r, c):
        return (r - 1) * cols + (c - 1)

    transform = build_clip_by_indices(frames, [idx(4, 1), idx(1, 1)], fps=10, loop=False)
    idle = build_clip_by_indices(frames, [idx(1, c) for c in range(1, 5)], fps=8, loop=True)
    walk = build_clip_by_indices(frames, [idx(2, c) for c in range(1, 5)], fps=8, loop=True)
    atk = build_clip_by_indices(frames, [idx(3, c) for c in range(1, 7)], fps=12, loop=False)
    hit = build_clip_by_indices(frames, [idx(4, c) for c in range(1, 4)], fps=12, loop=False)
    i_move = build_clip_by_indices(frames, [idx(6, c) for c in range(1, 9)], fps=12, loop=False)

    return idle, walk, transform, atk, i_move, hit


def load_fireball_frames():
    surface = pg.image.load(FIREBALL_SHEET).convert_alpha()
    frames_raw = slice_sheet(surface, FIREBALL_FRAME_W, FIREBALL_FRAME_H)

    cols = surface.get_width() // FIREBALL_FRAME_W

    def idx(r, c):
        return (r - 1) * cols + (c - 1)

    anim_idx = [idx(4, c) for c in range(1, 6)]
    frames = [scale_to_h(frames_raw[i], 48) for i in anim_idx]

    return frames