import pygame as pg

from settings import (
    STATE_GHOST,
    STATE_GHOST_ATK,
    STATE_ATK,
    STATE_BLOCK,
    STATE_HIT,
    STATE_BEAST_ATK,
    STATE_BEAST,
    STATE_IDLE,
    STATE_AIR,
)


def x_overlaps_rect(x, fw, rect: pg.Rect) -> bool:
    s_left, s_right = x, x + fw
    return (s_right > rect.left) and (s_left < rect.right)


def ghost_floor_y_under(floor_top):
    def _ghost_floor_y_under(_x, _fw, feet_off):
        return floor_top + feet_off
    return _ghost_floor_y_under


def fighter_landing_y(F, fw, fh, block1_rect, block2_rect, small1_rect, small2_rect):
    """
    Return the Y (top + feet_offset) of the surface the fighter should land on this frame,
    considering one-way floating platforms and solid bottom blocks.
    None if no landing.
    """
    bottom_now = F.y + fh
    feet_off = F.feet_offset()

    candidate_y = None

    # Main blocks
    for rect in (block1_rect, block2_rect):
        if x_overlaps_rect(F.x, fw, rect):
            gy = rect.top + feet_off
            # Land if falling and crossing its top, or keep standing if already placed on it
            if F.vy >= 0 and bottom_now >= gy and F.prev_bottom <= gy + 2:
                candidate_y = gy if (candidate_y is None or gy < candidate_y) else candidate_y

    # Floating one-way platforms
    for rect in (small1_rect, small2_rect):
        if x_overlaps_rect(F.x, fw, rect):
            gy = rect.top + feet_off - 35
            # Must be falling and coming from above the top to land
            if F.vy >= 0 and F.prev_bottom <= gy + 2 and bottom_now >= gy:
                candidate_y = gy if (candidate_y is None or gy < candidate_y) else candidate_y

    return candidate_y


def land_if_possible(F, fw, fh, landing_func, block1_rect, block2_rect, small1_rect, small2_rect):
    if F.state in (STATE_GHOST, STATE_GHOST_ATK):
        return

    gy = landing_func(F, fw, fh, block1_rect, block2_rect, small1_rect, small2_rect)

    if gy is not None and F.vy >= 0 and F.y + fh >= gy:
        F.y = gy - fh
        F.vy = 0.0
        if not F.grounded:
            F.grounded = True
            if F.state not in (STATE_ATK, STATE_BLOCK, STATE_HIT, STATE_BEAST_ATK):
                F.state = STATE_BEAST if F.beast_active else STATE_IDLE
                F.anim = F.beast_idle_clip if F.beast_active else F.idle_clip
                F.anim.reset()
    else:
        support_now = (gy is not None) and (abs((F.y + fh) - gy) <= 1.0)
        if not support_now:
            if F.grounded:
                F.grounded = False
                if F.state not in (STATE_ATK, STATE_BLOCK, STATE_HIT, STATE_BEAST_ATK):
                    F.state = STATE_AIR
                    F.anim = F.beast_idle_clip if F.beast_active else F.idle_clip
                    F.anim.reset()