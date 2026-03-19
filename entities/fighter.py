import pygame as pg

from settings import (
    STATE_IDLE,
    STATE_WALK,
    STATE_ATK,
    STATE_AIR,
    STATE_BLOCK,
    STATE_HIT,
    STATE_GHOST,
    STATE_GHOST_ATK,
    STATE_BEAST,
    STATE_BEAST_ATK,
    GHOST_ATK_VULN_MULT,
    METER_COST_COMBO,
    GHOST_MIN_TO_START,
    GHOST_ATK_COST,
    FEET_OFFSET,
    GHOST_DRAIN_RATE,
    GHOST_BOOST_EXTRA_DRAIN,
    METER_GAIN_RATE,
    GHOST_BOOST_SPEED_MULT,
    GHOST_SPEED,
    WIN_W,
    CLAMP_MARGIN,
    HITBOX_INSET_Y,
    HITBOX_DEPTH,
    GHOST_ATK_AURA_INFLATE,
    BEAST_SPEED_MULT,
    JUMP_VELOCITY,
)
from animations import clamp_draw_x


class Fighter:
    def __init__(
            self,
            frames,
            idle_clip,
            walk_clip,
            punch_clip,
            kick_clip,
            block_clip,
            combo_clip,
            hit_clip,
            ghost_idle_clip,
            ghost_transform_clip,
            ghost_attack_clip,
            beast_idle_clip=None,
            beast_walk_clip=None,
            beast_transform_clip=None,
            beast_attack_clip=None,
            beast_special_clip=None,
            beast_i_clip=None,
            beast_hit_clip=None,
            start_x=0,
            start_y=0,
            facing=1,
            name="",
    ):
        self.name = name
        self.frames = frames
        self.idle_clip = idle_clip
        self.walk_clip = walk_clip
        self.punch_clip = punch_clip
        self.kick_clip = kick_clip
        self.block_clip = block_clip
        self.combo_clip = combo_clip
        self.hit_clip = hit_clip
        self.ghost_idle_clip = ghost_idle_clip
        self.ghost_transform_clip = ghost_transform_clip
        self.ghost_attack_clip = ghost_attack_clip

        self.beast_idle_clip = beast_idle_clip
        self.beast_walk_clip = beast_walk_clip
        self.beast_transform_clip = beast_transform_clip
        self.beast_attack_clip = beast_attack_clip
        self.beast_special_clip = beast_special_clip
        self.beast_i_clip = beast_i_clip
        self.beast_hit_clip = beast_hit_clip
        self.beast_active = False

        self.x = start_x
        self.y = start_y
        self.vx = 0.0
        self.vy = 0.0
        self.grounded = True

        self.facing = facing
        self.state = STATE_IDLE
        self.anim = self.idle_clip
        self.atk_anim = None

        self.blocking = False

        self.hit_registered = False
        self.combo_stages_hit = set()

        self.meter = 0.0
        self.vuln_timer = 0.0
        self.aura_timer = 0.0

        self.prev_bottom = 0.0

    def vuln_mult(self):
        mult = GHOST_ATK_VULN_MULT if self.vuln_timer > 0.0 else 1.0
        return mult

    def can_use_combo(self):
        return self.meter >= METER_COST_COMBO

    def consume_combo_meter(self):
        self.meter = max(0.0, self.meter - METER_COST_COMBO)

    def start_punch(self):
        if self.state in (STATE_ATK, STATE_BLOCK, STATE_HIT, STATE_GHOST, STATE_GHOST_ATK):
            return
        if self.beast_active:
            self.state = STATE_BEAST_ATK
            self.atk_anim = self.beast_attack_clip
            self.atk_anim.reset()
            self.anim = self.atk_anim
            self.hit_registered = False
            return
        self.state = STATE_ATK
        self.atk_anim = self.punch_clip
        self.atk_anim.reset()
        self.anim = self.atk_anim
        self.hit_registered = False
        self.combo_stages_hit.clear()

    def start_kick(self):
        if self.state in (STATE_ATK, STATE_BLOCK, STATE_HIT, STATE_GHOST, STATE_GHOST_ATK):
            return
        if self.beast_active:
            self.state = STATE_BEAST_ATK
            self.atk_anim = self.beast_attack_clip
            self.atk_anim.reset()
            self.anim = self.atk_anim
            self.hit_registered = False
            return
        self.state = STATE_ATK
        self.atk_anim = self.kick_clip
        self.atk_anim.reset()
        self.anim = self.atk_anim
        self.hit_registered = False
        self.combo_stages_hit.clear()

    def start_combo(self):
        if self.state in (STATE_ATK, STATE_BLOCK, STATE_HIT, STATE_GHOST, STATE_GHOST_ATK):
            return
        if self.beast_active:
            return
        if not self.can_use_combo():
            return
        self.consume_combo_meter()
        self.state = STATE_ATK
        self.atk_anim = self.combo_clip
        self.atk_anim.reset()
        self.anim = self.atk_anim
        self.hit_registered = False
        self.combo_stages_hit.clear()

    def start_block(self):
        if self.blocking:
            return
        if self.beast_active:
            return
        if not self.grounded or self.state in (STATE_ATK, STATE_HIT, STATE_GHOST, STATE_GHOST_ATK):
            return
        self.blocking = True
        self.state = STATE_BLOCK
        she = self.block_clip
        she.reset()
        self.anim = she

    def stop_block(self):
        if not self.blocking:
            return
        self.blocking = False
        if self.grounded:
            self.state, self.anim = STATE_IDLE, self.idle_clip
        else:
            self.state, self.anim = STATE_AIR, self.idle_clip
        self.anim.reset()

    def start_hit(self):
        if self.state in (STATE_GHOST, STATE_GHOST_ATK):
            return
        self.state = STATE_HIT
        self.anim = self.beast_hit_clip if self.beast_active and self.beast_hit_clip else self.hit_clip
        self.anim.reset()
        self.atk_anim = None
        self.hit_registered = False
        self.combo_stages_hit.clear()

    def toggle_ghost(self):
        if self.beast_active:
            return
        if self.state == STATE_GHOST:
            self.end_ghost()
        else:
            self.start_ghost()

    def start_ghost(self):
        if self.meter < GHOST_MIN_TO_START:
            return
        self.state = STATE_GHOST
        self.anim = self.ghost_transform_clip
        self.anim.reset()
        self.atk_anim = None
        self.blocking = False
        self.vy = 0.0
        self.grounded = False

    def end_ghost(self):
        self.state = STATE_AIR if not self.grounded else STATE_IDLE
        self.anim = self.idle_clip
        self.anim.reset()

    def start_ghost_attack(self):
        if self.state != STATE_GHOST:
            return
        if self.meter < GHOST_ATK_COST:
            return
        self.meter = max(0.0, self.meter - GHOST_ATK_COST)
        self.state = STATE_GHOST_ATK
        self.anim = self.ghost_attack_clip
        self.anim.reset()
        self.atk_anim = None
        self.hit_registered = False

    def toggle_beast(self):
        if self.state in (STATE_GHOST, STATE_GHOST_ATK):
            return
        if not self.beast_idle_clip:
            return
        if self.beast_active:
            self.end_beast()
        else:
            self.start_beast()

    def start_beast(self):
        old_offset = self.feet_offset()

        self.beast_active = True
        new_offset = self.feet_offset()

        if self.grounded:
            self.y += (new_offset - old_offset)

        self.state = STATE_BEAST
        self.anim = self.beast_transform_clip
        self.anim.reset()
        self.atk_anim = None
        self.blocking = False

    def end_beast(self):
        old_offset = self.feet_offset()

        self.beast_active = False
        new_offset = self.feet_offset()

        if self.grounded:
            self.y += (new_offset - old_offset)

        self.state = STATE_AIR if not self.grounded else STATE_IDLE
        self.anim = self.idle_clip
        self.anim.reset()

    def start_beast_special(self):
        if not self.beast_active:
            return
        if self.state in (STATE_ATK, STATE_BLOCK, STATE_HIT, STATE_GHOST, STATE_GHOST_ATK):
            return
        self.state = STATE_BEAST_ATK
        self.atk_anim = self.beast_special_clip
        self.atk_anim.reset()
        self.anim = self.atk_anim
        self.hit_registered = False

    def start_beast_I(self):
        if not self.beast_active or not self.beast_i_clip:
            return
        if self.state in (STATE_ATK, STATE_BLOCK, STATE_HIT, STATE_GHOST, STATE_GHOST_ATK):
            return
        self.state = STATE_BEAST_ATK
        self.atk_anim = self.beast_i_clip
        self.atk_anim.reset()
        self.anim = self.atk_anim
        self.hit_registered = False

    def set_walk(self, moving):
        if self.state in (STATE_ATK, STATE_BLOCK, STATE_HIT, STATE_GHOST, STATE_GHOST_ATK, STATE_BEAST_ATK):
            return

        desired_state = STATE_WALK if moving else (STATE_AIR if not self.grounded else STATE_IDLE)

        if self.beast_active and self.state in (STATE_BEAST, STATE_WALK, STATE_IDLE, STATE_AIR):
            desired_anim = self.beast_walk_clip if moving and self.beast_walk_clip else self.beast_idle_clip
        else:
            desired_anim = self.walk_clip if moving else self.idle_clip

        if self.state != desired_state or self.anim is not desired_anim:
            self.state, self.anim = desired_state, desired_anim
            self.anim.reset()

    def jump(self):
        if self.beast_active:
            return
        if self.state in (STATE_ATK, STATE_BLOCK, STATE_HIT, STATE_GHOST, STATE_GHOST_ATK):
            return
        if self.grounded:
            self.vy = JUMP_VELOCITY
            self.grounded = False
            self.state, self.anim = STATE_AIR, self.idle_clip
            self.anim.reset()

    def feet_offset(self) -> int:
        return FEET_OFFSET - (6 if self.beast_active else 0)

    def update(self, dt, ghost_floor_func, fw, fh, is_p1):
        keys = pg.key.get_pressed()
        boosting = False

        if self.state in (STATE_GHOST, STATE_GHOST_ATK):
            boosting = keys[pg.K_u] if is_p1 else keys[pg.K_KP5]
            drain = GHOST_DRAIN_RATE + (GHOST_BOOST_EXTRA_DRAIN if boosting else 0.0)
            self.meter = max(0.0, self.meter - drain * dt)
            if self.meter <= 0.0 and self.state == STATE_GHOST:
                self.end_ghost()
        else:
            self.meter = min(1.0, self.meter + METER_GAIN_RATE * dt)

        if self.vuln_timer > 0.0:
            self.vuln_timer = max(0.0, self.vuln_timer - dt)

        if self.aura_timer > 0.0:
            self.aura_timer = max(0.0, self.aura_timer - dt)

        self.anim.update(dt)

        if self.state in (STATE_ATK, STATE_BEAST_ATK) and self.atk_anim:
            if self.atk_anim.done:
                if self.beast_active:
                    self.state = STATE_BEAST
                    self.anim = self.beast_idle_clip
                else:
                    self.state = STATE_AIR if not self.grounded else STATE_IDLE
                    self.anim = self.idle_clip
                self.anim.reset()
                self.atk_anim = None
                self.hit_registered = False
                self.combo_stages_hit.clear()

        elif self.state == STATE_HIT and self.anim.done:
            self.state = STATE_AIR if not self.grounded else STATE_IDLE
            self.anim = self.beast_idle_clip if self.beast_active else self.idle_clip
            self.anim.reset()

        elif self.state == STATE_GHOST:
            if self.anim.done and self.anim is self.ghost_transform_clip:
                self.anim = self.ghost_idle_clip
                self.anim.reset()

        elif self.state == STATE_GHOST_ATK:
            if self.anim.done:
                self.end_ghost()

        elif self.state == STATE_BEAST:
            if self.anim is self.beast_transform_clip and self.anim.done:
                self.anim = self.beast_idle_clip
                self.anim.reset()

        gy = ghost_floor_func(self.x, fw, self.feet_offset())
        if gy is None:
            from settings import WIN_H
            gy = WIN_H

        if self.state in (STATE_GHOST, STATE_GHOST_ATK):
            if is_p1:
                gx = (1 if keys[pg.K_d] else 0) - (1 if keys[pg.K_a] else 0)
                gyk = (1 if keys[pg.K_s] else 0) - (1 if keys[pg.K_w] else 0)
            else:
                gx = (1 if keys[pg.K_RIGHT] else 0) - (1 if keys[pg.K_LEFT] else 0)
                gyk = (1 if keys[pg.K_DOWN] else 0) - (1 if keys[pg.K_UP] else 0)

            speed = GHOST_SPEED * (GHOST_BOOST_SPEED_MULT if boosting else 1.0)
            self.x += gx * speed * dt
            self.y += gyk * speed * dt
            self.x = clamp_draw_x(self.x, fw, WIN_W, CLAMP_MARGIN)
            self.y = max(0, min(gy - fh, self.y))

    def current_frame(self):
        return self.anim.get()

    def bbox(self):
        f = self.current_frame()
        if not f:
            return pg.Rect(int(self.x), int(self.y), 0, 0)
        w, h = f.get_size()
        return pg.Rect(int(self.x), int(self.y), w, h)

    def attack_hitbox(self):
        if self.state in (STATE_ATK, STATE_BEAST_ATK) and self.atk_anim:
            f = self.current_frame()
            if not f:
                return None
            w, h = f.get_size()
            top = int(self.y) + HITBOX_INSET_Y
            height = max(4, h - 2 * HITBOX_INSET_Y)
            if self.facing == 1:
                return pg.Rect(int(self.x) + w, top, HITBOX_DEPTH, height)
            else:
                return pg.Rect(int(self.x) - HITBOX_DEPTH, top, HITBOX_DEPTH, height)

        if self.state == STATE_GHOST_ATK:
            rect = self.bbox().copy()
            rect.inflate_ip(*GHOST_ATK_AURA_INFLATE)
            return rect

        return None

    def current_attack_stage(self):
        if self.state not in (STATE_ATK, STATE_BEAST_ATK) or not self.atk_anim:
            return (None, None)
        if self.atk_anim is self.punch_clip:
            return ("punch", None)
        if self.atk_anim is self.kick_clip:
            return ("kick", None)
        if self.atk_anim is self.combo_clip:
            total = max(1, self.atk_anim.len())
            stage = min((self.atk_anim.i * 4) // total, 3)
            return ("combo", stage)
        if self.atk_anim is self.beast_attack_clip:
            return ("beast_atk", None)
        if self.atk_anim is self.beast_special_clip:
            return ("beast_sp", None)
        if self.atk_anim is self.beast_i_clip:
            return ("beast_i", None)
        return (None, None)
