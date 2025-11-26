import pygame as pg
import random as rnd  # for fireball spawning

# ---------- Assets ----------
SKY_PATH = "graphics/back.png"
SUN_PATH = "graphics/cethiel-desert-edit-small-swm-version-layer3.png"
BLOCK_PATH = "graphics/brown platform merged transparent.png"
P1_SHEET = "graphics/fighter_base/cat_fighter_sprite1.png"
P2_SHEET = "graphics/fighter_base/cat_fighter_sprite2.png"
GHOST_SHEET = "graphics/ghost_base/mon3_sprite_base.png"
START_IMG_PATH = "graphics/cat_walk_shot.gif"

# --- BEAST sheets (P1 + P2) ---
BEAST_SHEET = "graphics/p1_beast_base/mon2_sprite_base.png"
P2_BEAST_SHEET = "graphics/p2_beast_base/mon1_sprite_addon_2012_12_14.png"

# ---------- Fighter sprite sheet ----------
FRAME_W, FRAME_H = 50, 50
SHEET_COLS = 10
TARGET_CHAR_H = 110

# Anim ranges
IDLE_START_INDEX = 5
IDLE_FRAME_COUNT = 2
WALK_START_INDEX = 3
WALK_FRAME_COUNT = 2


def rc_to_indices(row1, col1, col2, cols=SHEET_COLS, reverse=False):
    r0 = row1 - 1
    seq = [r0 * cols + (c - 1) for c in range(col1, col2 + 1)]
    return list(reversed(seq)) if reverse else seq


PUNCH_IDX = rc_to_indices(4, 8, 10)
KICK_IDX = rc_to_indices(1, 7, 10)
BLOCK_IDX = rc_to_indices(6, 1, 2)
COMBO_IDX = rc_to_indices(5, 1, 10) + rc_to_indices(6, 5, 10)
HIT_IDX = rc_to_indices(1, 1, 3)

# Ghost sprite sheet tile size
GHOST_FRAME_W = 64
GHOST_FRAME_H = 64

# BEAST sprite sheet tile size
BEAST_FRAME_W = 64
BEAST_FRAME_H = 64

# Movement / clamp
MOVE_SPEED = 360.0  # per-second walking speed (dt-based)
CLAMP_MARGIN = 10

# Jump / gravity
GRAVITY_PX_S2 = 2600.0
JUMP_VELOCITY = -900.0

# Damage (1.0 == full health bar)
DMG_PUNCH = 0.04
DMG_KICK = 0.048
DMG_COMBO = [0.05, 0.10, 0.10, 0.05]
BLOCK_MULTIPLIER = 0.1

# BEAST: damage & speed multipliers
BEAST_DMG_MULT = 1.25
BEAST_SPEED_MULT = 1.35

# Beast attack damages
DMG_BEAST_ATK = 0.06  # before multiplier
DMG_BEAST_SP = 0.08  # before multiplier
DMG_BEAST_I = 0.10  # Beast “I” move base damage (before multiplier)

# Hitbox shape
HITBOX_DEPTH = 30
HITBOX_INSET_Y = 20
DEBUG_HITBOXES = False

# UI colors
P1_COLOR = (90, 200, 255)
P2_COLOR = (255, 160, 80)
UI_WHITE = (245, 245, 245)

# Window
WIN_W, WIN_H = 1280, 720

# Ground
GROUND_DROP = 80
FEET_OFFSET = 82

# Meter
METER_GAIN_RATE = 0.10
METER_COST_COMBO = 1.0 / 3.0

# Ghost form
STATE_GHOST = "GHOST"
GHOST_SPEED = 260.0
GHOST_DRAIN_RATE = 0.05
GHOST_MIN_TO_START = 0.05

# Ghost boost
GHOST_BOOST_SPEED_MULT = 2.2
GHOST_BOOST_EXTRA_DRAIN = 0.50

# Ghost attack
STATE_GHOST_ATK = "GHOST_ATK"
GHOST_ATK_COST = 0.20
GHOST_ATK_VULN_MULT = 1.05
GHOST_ATK_VULN_SECS = 6.0
GHOST_ATK_AURA_INFLATE = (28, 18)

# BEAST states
STATE_BEAST = "BEAST"
STATE_BEAST_ATK = "BEAST_ATK"

# Fireball (projectile)
FIREBALL_SHEET = "graphics/energy_effect_base.png"
FIREBALL_FRAME_W = 32
FIREBALL_FRAME_H = 32
FIREBALL_SPEED = 420.0
FIREBALL_DAMAGE = 0.06
FIREBALL_SPAWN_MIN = 1.6
FIREBALL_SPAWN_MAX = 3.2


#  helpers
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


def scale_to_h(s: pg.Surface, h: int) -> pg.Surface:
    w, oh = s.get_size()
    return pg.transform.smoothscale(s, (int(w * h / oh), h))


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
        if not self.frames or self.done: return
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


def blit_faced(surf, frame, pos, facing):
    if facing == -1:
        frame = pg.transform.flip(frame, True, False)
    surf.blit(frame, pos)


def clamp_draw_x(x, fw, W, margin=0):
    return max(margin, min(W - margin - fw, x))


def draw_bar(screen, x, y, w, h, pct, color, border_col=(10, 10, 15), bg_col=(50, 50, 60)):
    pct = max(0.0, min(1.0, pct))
    pg.draw.rect(screen, bg_col, (x, y, w, h), border_radius=8)
    pg.draw.rect(screen, color, (x + 3, y + 3, int((w - 6) * pct), h - 6), border_radius=8)
    pg.draw.rect(screen, border_col, (x, y, w, h), 2, border_radius=8)


def draw_health_and_meter(screen, x, y, w, h, hp, meter, color, label, font):
    draw_bar(screen, x, y, w, h, hp, color)
    screen.blit(font.render(label, True, UI_WHITE), (x, y - 20))
    draw_bar(screen, x, y + h + 6, w, int(h * 0.6), meter, (180, 120, 255))


# Fighter state
STATE_IDLE = "IDLE"
STATE_WALK = "WALK"
STATE_ATK = "ATTACK"
STATE_AIR = "AIR"
STATE_BLOCK = "BLOCK"
STATE_HIT = "HIT"


class Fighter:
    def __init__(self, frames, idle_clip, walk_clip, punch_clip, kick_clip, block_clip, combo_clip, hit_clip,
                 ghost_idle_clip, ghost_transform_clip, ghost_attack_clip,
                 # --- BEAST clips (optional per player) ---
                 beast_idle_clip=None, beast_walk_clip=None, beast_transform_clip=None, beast_attack_clip=None,
                 beast_special_clip=None,
                 beast_i_clip=None, beast_hit_clip=None,
                 start_x=0, start_y=0, facing=1, name=""):
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

        # --- BEAST refs ---
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

        # Aura VFX timer for Beast-I land
        self.aura_timer = 0.0

        # Track previous bottom to enable one-way platform landing
        self.prev_bottom = 0.0

    def vuln_mult(self):
        mult = GHOST_ATK_VULN_MULT if self.vuln_timer > 0.0 else 1.0
        return mult

    def can_use_combo(self):
        return self.meter >= METER_COST_COMBO

    def consume_combo_meter(self):
        self.meter = max(0.0, self.meter - METER_COST_COMBO)

    # Core actions
    def start_punch(self):
        if self.state in (STATE_ATK, STATE_BLOCK, STATE_HIT, STATE_GHOST, STATE_GHOST_ATK): return
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
        if self.state in (STATE_ATK, STATE_BLOCK, STATE_HIT, STATE_GHOST, STATE_GHOST_ATK): return
        if self.beast_active:
            # In Beast form, treat kick as the same primary Beast attack
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
        if self.state in (STATE_ATK, STATE_BLOCK, STATE_HIT, STATE_GHOST, STATE_GHOST_ATK): return
        if self.beast_active:
            return
        if not self.can_use_combo(): return
        self.consume_combo_meter()
        self.state = STATE_ATK
        self.atk_anim = self.combo_clip
        self.atk_anim.reset()
        self.anim = self.atk_anim
        self.hit_registered = False
        self.combo_stages_hit.clear()

    def start_block(self):
        if self.blocking: return
        if self.beast_active:  # --- BEAST: cannot block
            return
        if not self.grounded or self.state in (STATE_ATK, STATE_HIT, STATE_GHOST, STATE_GHOST_ATK): return
        self.blocking = True
        self.state = STATE_BLOCK
        she = self.block_clip
        she.reset()
        self.anim = she

    def stop_block(self):
        if not self.blocking: return
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
        # Use beast-specific hit if active
        self.anim = (self.beast_hit_clip if self.beast_active and self.beast_hit_clip else self.hit_clip)
        self.anim.reset()
        self.atk_anim = None
        self.hit_registered = False
        self.combo_stages_hit.clear()

    # ---------- Ghost ----------
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

    # ---------- BEAST ----------
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
        self.beast_active = True
        self.state = STATE_BEAST
        self.anim = self.beast_transform_clip
        self.anim.reset()
        self.atk_anim = None
        self.blocking = False

    def end_beast(self):
        self.beast_active = False
        self.state = STATE_AIR if not self.grounded else STATE_IDLE
        self.anim = self.idle_clip
        self.anim.reset()

    def start_beast_special(self):
        if not self.beast_active: return
        if self.state in (STATE_ATK, STATE_BLOCK, STATE_HIT, STATE_GHOST, STATE_GHOST_ATK):
            return
        self.state = STATE_BEAST_ATK
        self.atk_anim = self.beast_special_clip
        self.atk_anim.reset()
        self.anim = self.atk_anim
        self.hit_registered = False

    # Beast “I” move debug
    def start_beast_I(self):
        if not self.beast_active or not self.beast_i_clip: return
        if self.state in (STATE_ATK, STATE_BLOCK, STATE_HIT, STATE_GHOST, STATE_GHOST_ATK): return
        self.state = STATE_BEAST_ATK
        self.atk_anim = self.beast_i_clip
        self.atk_anim.reset()
        self.anim = self.atk_anim
        self.hit_registered = False

    def set_walk(self, moving):
        if self.state in (STATE_ATK, STATE_BLOCK, STATE_HIT, STATE_GHOST, STATE_GHOST_ATK, STATE_BEAST_ATK): return
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
        if self.state in (STATE_ATK, STATE_BLOCK, STATE_HIT, STATE_GHOST, STATE_GHOST_ATK): return
        if self.grounded:
            self.vy = JUMP_VELOCITY
            self.grounded = False
            self.state, self.anim = STATE_AIR, self.idle_clip
            self.anim.reset()

    def feet_offset(self) -> int:
        """Pixels from platform top to fighter feet for current form."""
        # Beast sprite sits a bit lower visually; nudge up 6 px
        return FEET_OFFSET - (6 if self.beast_active else 0)

    def update(self, dt, ghost_floor_func, fw, fh, is_p1):
        # Meter update
        keys = pg.key.get_pressed()
        boosting = False
        if self.state in (STATE_GHOST, STATE_GHOST_ATK):
            boosting = (keys[pg.K_u] if is_p1 else keys[pg.K_KP5])
            drain = GHOST_DRAIN_RATE + (GHOST_BOOST_EXTRA_DRAIN if boosting else 0.0)
            self.meter = max(0.0, self.meter - drain * dt)
            if self.meter <= 0.0 and self.state == STATE_GHOST:
                self.end_ghost()
        else:
            self.meter = min(1.0, self.meter + METER_GAIN_RATE * dt)

        # Debuff timer
        if self.vuln_timer > 0.0:
            self.vuln_timer = max(0.0, self.vuln_timer - dt)

        # Aura timer
        if self.aura_timer > 0.0:
            self.aura_timer = max(0.0, self.aura_timer - dt)

        self.anim.update(dt)

        # Attack lifecycles
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

        # Ghost movement clamp (ghost ignores floating platforms)
        gy = ghost_floor_func(self.x, fw, self.feet_offset())
        if gy is None: gy = WIN_H
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
        if not f: return pg.Rect(int(self.x), int(self.y), 0, 0)
        w, h = f.get_size()
        return pg.Rect(int(self.x), int(self.y), w, h)

    def attack_hitbox(self):
        # Normal / Beast attacks
        if (self.state in (STATE_ATK, STATE_BEAST_ATK)) and self.atk_anim:
            f = self.current_frame()
            if not f: return None
            w, h = f.get_size()
            top = int(self.y) + HITBOX_INSET_Y
            height = max(4, h - 2 * HITBOX_INSET_Y)
            if self.facing == 1:
                return pg.Rect(int(self.x) + w, top, HITBOX_DEPTH, height)
            else:
                return pg.Rect(int(self.x) - HITBOX_DEPTH, top, HITBOX_DEPTH, height)

        # Ghost attack aura
        if self.state == STATE_GHOST_ATK:
            rect = self.bbox().copy()
            rect.inflate_ip(*GHOST_ATK_AURA_INFLATE)
            return rect
        return None

    def current_attack_stage(self):
        if self.state not in (STATE_ATK, STATE_BEAST_ATK) or not self.atk_anim: return (None, None)
        if self.atk_anim is self.punch_clip: return ("punch", None)
        if self.atk_anim is self.kick_clip:  return ("kick", None)
        if self.atk_anim is self.combo_clip:
            total = max(1, self.atk_anim.len())
            stage = min((self.atk_anim.i * 4) // total, 3)
            return ("combo", stage)
        if self.atk_anim is self.beast_attack_clip:  return ("beast_atk", None)
        if self.atk_anim is self.beast_special_clip: return ("beast_sp", None)
        if self.atk_anim is self.beast_i_clip:      return ("beast_i", None)
        return (None, None)


# Fireball projectile
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
        if not fr: return pg.Rect(int(self.x), int(self.y), 0, 0)
        w, h = fr.get_size()
        return pg.Rect(int(self.x), int(self.y), w, h)

    def draw(self, screen):
        fr = self.frame()
        if not fr: return
        # flip to face movement (visual only)
        if self.vx < 0:
            fr = pg.transform.flip(fr, True, False)
        screen.blit(fr, (int(self.x), int(self.y)))


#  Damage helper
def apply_damage(attacker, defender, base_dmg, hit_flag=False, combo_stage=None):
    global p1_hp, p2_hp
    if defender.state in (STATE_GHOST, STATE_GHOST_ATK):
        return

    dmg = base_dmg * (BLOCK_MULTIPLIER if defender.blocking else 1.0)

    # Beast bonus if attacker is a Fighter in Beast
    if isinstance(attacker, Fighter) and attacker.beast_active:
        dmg *= BEAST_DMG_MULT

    # Vulnerability debuff only for normal Fighter attacks
    if isinstance(attacker, Fighter) and attacker.state not in (STATE_GHOST, STATE_GHOST_ATK):
        dmg *= defender.vuln_mult()

    if defender.name == "P1":
        p1_hp = max(0.0, p1_hp - dmg)
    elif defender.name == "P2":
        p2_hp = max(0.0, p2_hp - dmg)

    if isinstance(attacker, Fighter) and hit_flag:
        attacker.hit_registered = True
    if isinstance(attacker, Fighter) and combo_stage is not None:
        attacker.combo_stages_hit.add(combo_stage)

    if not defender.blocking and dmg > 0:
        defender.start_hit()


def show_start_screen(screen, win_w, win_h):
    img = pg.image.load(START_IMG_PATH).convert_alpha()
    bg_color = img.get_at((0, 0))[:3]

    scale_factor = 6
    big = pg.transform.smoothscale(img, (img.get_width() * scale_factor, img.get_height() * scale_factor))


    title_font = pg.font.SysFont("consolas", 48, bold=True)
    hint_font = pg.font.SysFont("consolas", 28)


    title = title_font.render("Press SPACE to Start", True, (255, 255, 255))
    hint = hint_font.render("ESC to Quit", True, (230, 230, 230))

    clock = pg.time.Clock()
    waiting = True
    while waiting:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit();
                raise SystemExit
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    pg.quit();
                    raise SystemExit
                if e.key == pg.K_SPACE:
                    waiting = False


        screen.fill(bg_color)

        bx = (win_w - big.get_width()) // 2
        by = (win_h - big.get_height()) // 2 - 40
        screen.blit(big, (bx, by))

        # center the text under the image
        tx = (win_w - title.get_width()) // 2
        ty = by + big.get_height() + 10
        screen.blit(title, (tx, ty))

        hx = (win_w - hint.get_width()) // 2
        hy = ty + title.get_height() + 8
        screen.blit(hint, (hx, hy))

        pg.display.flip()
        clock.tick(60)


def show_winner_screen(screen, text):

    img = pg.image.load(START_IMG_PATH).convert_alpha()
    bg = img.get_at((0, 0))[:3]


    big = pg.transform.smoothscale(img, (img.get_width() * 6, img.get_height() * 6))

    title_font = pg.font.SysFont("consolas", 56, bold=True)
    hint_font = pg.font.SysFont("consolas", 28)

    title = title_font.render(text, True, (255, 255, 255))
    hint = hint_font.render("Press SPACE for New Game", True, (230, 230, 230))

    clock = pg.time.Clock()
    waiting = True
    while waiting:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit();
                raise SystemExit
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    pg.quit();
                    raise SystemExit
                if e.key == pg.K_SPACE:
                    waiting = False

        screen.fill(bg)
        bx = (WIN_W - big.get_width()) // 2
        by = (WIN_H - big.get_height()) // 2 - 40
        screen.blit(big, (bx, by))

        tx = (WIN_W - title.get_width()) // 2
        ty = by + big.get_height() + 12
        screen.blit(title, (tx, ty))

        hx = (WIN_W - hint.get_width()) // 2
        hy = ty + title.get_height() + 10
        screen.blit(hint, (hx, hy))

        pg.display.flip()
        clock.tick(60)


def main():
    pg.init()
    screen = pg.display.set_mode((WIN_W, WIN_H))
    pg.display.set_caption("Switch it down")
    show_start_screen(screen, WIN_W, WIN_H)

    # Background & stage
    sky = pg.transform.scale(pg.image.load(SKY_PATH).convert(), (WIN_W, WIN_H))
    sun = pg.transform.smoothscale(pg.image.load(SUN_PATH).convert_alpha(), (500, 500))
    block = pg.image.load(BLOCK_PATH).convert_alpha()

    # Ground platforms (bottom two big boulders remain as before)
    block_y = WIN_H - block.get_height() + 10 + GROUND_DROP
    block1_pos = (70, block_y)
    block2_pos = (WIN_W - block.get_width() - 70, block_y)
    block1_rect = block.get_rect(topleft=block1_pos)
    block2_rect = block.get_rect(topleft=block2_pos)


    small_block = pg.transform.rotozoom(block, 0, 0.25)
    small1_pos = (block1_pos[0] + 180, block1_pos[1] - 260)
    small2_pos = (WIN_W - small_block.get_width() - 220, block2_pos[1] - 320)
    small1_rect = small_block.get_rect(topleft=small1_pos)
    small2_rect = small_block.get_rect(topleft=small2_pos)


    floor_top = block_y

    frames1 = [scale_to_h(f, TARGET_CHAR_H) for f in
               slice_sheet(pg.image.load(P1_SHEET).convert_alpha(), FRAME_W, FRAME_H)]
    frames2 = [scale_to_h(f, TARGET_CHAR_H) for f in
               slice_sheet(pg.image.load(P2_SHEET).convert_alpha(), FRAME_W, FRAME_H)]

    p1_idle = build_clip(frames1, IDLE_START_INDEX, IDLE_FRAME_COUNT, fps=8, loop=True)
    p1_walk = build_clip(frames1, WALK_START_INDEX, WALK_FRAME_COUNT, fps=8, loop=True)
    p1_punch = build_clip_by_indices(frames1, PUNCH_IDX, fps=12, loop=False)
    p1_kick = build_clip_by_indices(frames1, KICK_IDX, fps=12, loop=False)
    p1_block = build_clip_by_indices(frames1, BLOCK_IDX, fps=6, loop=True)
    p1_combo = build_clip_by_indices(frames1, COMBO_IDX, fps=14, loop=False)
    p1_hit = build_clip_by_indices(frames1, HIT_IDX, fps=12, loop=False)

    p2_idle = build_clip(frames2, IDLE_START_INDEX, IDLE_FRAME_COUNT, fps=8, loop=True)
    p2_walk = build_clip(frames2, WALK_START_INDEX, WALK_FRAME_COUNT, fps=8, loop=True)
    p2_punch = build_clip_by_indices(frames2, PUNCH_IDX, fps=12, loop=False)
    p2_kick = build_clip_by_indices(frames2, KICK_IDX, fps=12, loop=False)
    p2_block = build_clip_by_indices(frames2, BLOCK_IDX, fps=6, loop=True)
    p2_combo = build_clip_by_indices(frames2, COMBO_IDX, fps=14, loop=False)
    p2_hit = build_clip_by_indices(frames2, HIT_IDX, fps=12, loop=False)

    # Ghost sheet
    ghost_surface = pg.image.load(GHOST_SHEET).convert_alpha()
    ghost_frames_raw = slice_sheet(ghost_surface, GHOST_FRAME_W, GHOST_FRAME_H)
    ghost_frames = [scale_to_h(f, TARGET_CHAR_H) for f in ghost_frames_raw]
    ghost_cols = ghost_surface.get_width() // GHOST_FRAME_W

    def gidx(r, c):
        return (r - 1) * ghost_cols + (c - 1)

    GHOST_TRANSFORM_IDX = [gidx(3, 5), gidx(1, 1)]
    GHOST_IDLE_IDX = [gidx(1, c) for c in range(1, 5 + 1)]
    GHOST_ATK_IDX = [gidx(2, c) for c in range(1, 5 + 1)]
    ghost_transform_clip = build_clip_by_indices(ghost_frames, GHOST_TRANSFORM_IDX, fps=10, loop=False)
    ghost_idle_clip = build_clip_by_indices(ghost_frames, GHOST_IDLE_IDX, fps=8, loop=True)
    ghost_attack_clip = build_clip_by_indices(ghost_frames, GHOST_ATK_IDX, fps=10, loop=False)

    # P1 BEAST: load & clips
    beast_surface = pg.image.load(BEAST_SHEET).convert_alpha()
    beast_frames_raw = slice_sheet(beast_surface, BEAST_FRAME_W, BEAST_FRAME_H)
    beast_frames = [scale_to_h(f, TARGET_CHAR_H) for f in beast_frames_raw]
    beast_cols = beast_surface.get_width() // BEAST_FRAME_W

    def bidx(r, c):
        return (r - 1) * beast_cols + (c - 1)


    BEAST_TRANSFORM_IDX = [bidx(4, 5), bidx(1, 1)]
    BEAST_IDLE_IDX = [bidx(1, c) for c in range(1, 4 + 1)]
    BEAST_WALK_IDX = [bidx(2, c) for c in range(1, 4 + 1)]
    BEAST_ATK_IDX = [bidx(3, c) for c in range(1, 5 + 1)]
    BEAST_SP_IDX = [bidx(3, c) for c in range(1, 6 + 1)]
    BEAST_I_IDX = [bidx(6, c) for c in range(1, beast_cols + 1)]
    BEAST_HIT_IDX = [bidx(4, c) for c in range(1, 4 + 1)]

    beast_transform_clip = build_clip_by_indices(beast_frames, BEAST_TRANSFORM_IDX, fps=10, loop=False)
    beast_idle_clip = build_clip_by_indices(beast_frames, BEAST_IDLE_IDX, fps=8, loop=True)
    beast_walk_clip = build_clip_by_indices(beast_frames, BEAST_WALK_IDX, fps=8, loop=True)
    beast_attack_clip = build_clip_by_indices(beast_frames, BEAST_ATK_IDX, fps=12, loop=False)
    beast_special_clip = build_clip_by_indices(beast_frames, BEAST_SP_IDX, fps=12, loop=False)
    beast_i_clip = build_clip_by_indices(beast_frames, BEAST_I_IDX, fps=12, loop=False)
    beast_hit_clip = build_clip_by_indices(beast_frames, BEAST_HIT_IDX, fps=12, loop=False)

    # P2 BEAST: load & clips
    p2_beast_surface = pg.image.load(P2_BEAST_SHEET).convert_alpha()
    p2_beast_frames_raw = slice_sheet(p2_beast_surface, BEAST_FRAME_W, BEAST_FRAME_H)
    p2_beast_frames = [scale_to_h(f, TARGET_CHAR_H) for f in p2_beast_frames_raw]
    p2_beast_cols = p2_beast_surface.get_width() // BEAST_FRAME_W

    def b2idx(r, c):
        return (r - 1) * p2_beast_cols + (c - 1)

    P2_BEAST_TRANSFORM_IDX = [b2idx(4, 1), b2idx(1, 1)]
    P2_BEAST_IDLE_IDX = [b2idx(1, c) for c in range(1, 4 + 1)]  # row1 1..4
    P2_BEAST_WALK_IDX = [b2idx(2, c) for c in range(1, 4 + 1)]  # row2 1..4
    P2_BEAST_ATK_IDX = [b2idx(3, c) for c in range(1, 6 + 1)]  # row3 1..6
    P2_BEAST_HIT_IDX = [b2idx(4, c) for c in range(1, 3 + 1)]  # row4 1..3
    P2_BEAST_I_IDX = [b2idx(6, c) for c in range(1, 8 + 1)]  # row6 1..8

    p2_beast_transform_clip = build_clip_by_indices(p2_beast_frames, P2_BEAST_TRANSFORM_IDX, fps=10, loop=False)
    p2_beast_idle_clip = build_clip_by_indices(p2_beast_frames, P2_BEAST_IDLE_IDX, fps=8, loop=True)
    p2_beast_walk_clip = build_clip_by_indices(p2_beast_frames, P2_BEAST_WALK_IDX, fps=8, loop=True)
    p2_beast_attack_clip = build_clip_by_indices(p2_beast_frames, P2_BEAST_ATK_IDX, fps=12, loop=False)
    p2_beast_i_clip = build_clip_by_indices(p2_beast_frames, P2_BEAST_I_IDX, fps=12, loop=False)
    p2_beast_hit_clip = build_clip_by_indices(p2_beast_frames, P2_BEAST_HIT_IDX, fps=12, loop=False)

    fw1_0, fh1_0 = p1_idle.get().get_size()
    fw2_0, fh2_0 = p2_idle.get().get_size()
    p1_start_x = block1_pos[0] + block.get_width() // 2 - fw1_0 // 2
    p2_start_x = block2_pos[0] + block.get_width() // 2 - fw2_0 // 2

    global p1_hp, p2_hp
    p1_hp = 1.0
    p2_hp = 1.0

    P1 = Fighter(frames1, p1_idle, p1_walk, p1_punch, p1_kick, p1_block, p1_combo, p1_hit,
                 ghost_idle_clip, ghost_transform_clip, ghost_attack_clip,
                 # P1 Beast clips
                 beast_idle_clip, beast_walk_clip, beast_transform_clip, beast_attack_clip, beast_special_clip,
                 beast_i_clip, beast_hit_clip,
                 p1_start_x, 0, facing=1, name="P1")

    P2 = Fighter(frames2, p2_idle, p2_walk, p2_punch, p2_kick, p2_block, p2_combo, p2_hit,
                 ghost_idle_clip, ghost_transform_clip, ghost_attack_clip,
                 # P2 Beast clips (NEW)
                 p2_beast_idle_clip, p2_beast_walk_clip, p2_beast_transform_clip, p2_beast_attack_clip, None,
                 p2_beast_i_clip, p2_beast_hit_clip,
                 p2_start_x, 0, facing=-1, name="P2")


    fb_surface = pg.image.load(FIREBALL_SHEET).convert_alpha()
    fb_frames_raw = slice_sheet(fb_surface, FIREBALL_FRAME_W, FIREBALL_FRAME_H)
    fb_cols = fb_surface.get_width() // FIREBALL_FRAME_W

    def fb_idx(r, c):
        return (r - 1) * fb_cols + (c - 1)

    FB_ANIM_IDX = [fb_idx(4, c) for c in range(1, 5 + 1)]
    fireball_frames = [scale_to_h(fb_frames_raw[i], 48) for i in FB_ANIM_IDX]


    fireballs = []
    next_fb_in = rnd.uniform(FIREBALL_SPAWN_MIN, FIREBALL_SPAWN_MAX)

    #  Platform helpers (one-way for floating blocks)
    def x_overlaps_rect(x, fw, rect: pg.Rect) -> bool:
        s_left, s_right = x, x + fw
        return (s_right > rect.left) and (s_left < rect.right)

    def ghost_floor_y_under(_x, _fw, feet_off):
        """Ghost only collides with the bottom floor (not floating platforms)."""
        return floor_top + feet_off

    def fighter_landing_y(F: Fighter, fw, fh):
        """
        Return the Y (top + feet_offset) of the surface the fighter should land on this frame,
        considering one-way floating platforms and solid bottom blocks. None if no landing.
        """
        bottom_now = F.y + fh
        feet_off = F.feet_offset()

        candidate_y = None


        for rect in (block1_rect, block2_rect):
            if x_overlaps_rect(F.x, fw, rect):
                gy = rect.top + feet_off
                # Land if falling and crossing its top, or keep standing if already placed on it
                if F.vy >= 0 and bottom_now >= gy and F.prev_bottom <= gy + 2:
                    candidate_y = gy if (candidate_y is None or gy < candidate_y) else candidate_y


        for rect in (small1_rect, small2_rect):
            if x_overlaps_rect(F.x, fw, rect):
                gy = rect.top + feet_off - 35
                # Must be falling and coming from strictly above the top to land
                if F.vy >= 0 and F.prev_bottom <= gy + 2 and bottom_now >= gy:
                    candidate_y = gy if (candidate_y is None or gy < candidate_y) else candidate_y

        return candidate_y


    g1 = block1_rect.top + P1.feet_offset()
    P1.y = g1 - fh1_0
    P1.grounded = True
    P1.prev_bottom = P1.y + fh1_0

    g2 = block2_rect.top + P2.feet_offset()
    P2.y = g2 - fh2_0
    P2.grounded = True
    P2.prev_bottom = P2.y + fh2_0

    font = pg.font.SysFont("consolas", 24)
    clock = pg.time.Clock()

    def reset_match():
        global p1_hp, p2_hp, fireballs, next_fb_in
        p1_hp = 1.0
        p2_hp = 1.0


        for F, start_x, fw, fh, rect in (
                (P1, p1_start_x, fw1_0, fh1_0, block1_rect),
                (P2, p2_start_x, fw2_0, fh2_0, block2_rect),
        ):
            F.beast_active = False
            F.vx = 0.0
            F.vy = 0.0
            F.meter = 0.0
            F.vuln_timer = 0.0
            F.blocking = False
            F.state = STATE_IDLE
            F.anim = F.idle_clip
            F.anim.reset()
            F.x = start_x
            gy = rect.top + F.feet_offset()
            F.y = gy - fh
            F.grounded = True
            F.prev_bottom = F.y + fh


        fireballs = []
        next_fb_in = rnd.uniform(FIREBALL_SPAWN_MIN, FIREBALL_SPAWN_MAX)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0


        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    running = False
                # Toggle forms
                elif e.key == pg.K_k:
                    P1.toggle_ghost()
                elif e.key == pg.K_KP3:
                    P2.toggle_ghost()
                elif e.key == pg.K_j:
                    P1.toggle_beast()
                elif e.key == pg.K_KP1:
                    P2.toggle_beast()

                # Attacks
                # P1
                elif e.key == pg.K_y:
                    if P1.state == STATE_GHOST:
                        P1.start_ghost_attack()
                    else:

                        P1.start_punch()
                elif e.key == pg.K_u:

                    if P1.beast_active:
                        P1.start_beast_special()
                    elif P1.state not in (STATE_GHOST, STATE_GHOST_ATK):
                        P1.start_kick()

                elif e.key == pg.K_i:
                    if P1.beast_active:
                        P1.start_beast_I()
                    else:
                        P1.start_combo()

                elif e.key == pg.K_w:
                    P1.jump()

                # P2 attacks
                elif e.key == pg.K_KP4:
                    if P2.state == STATE_GHOST:
                        P2.start_ghost_attack()
                    else:

                        P2.start_punch()
                elif e.key == pg.K_KP5:

                    if P2.state not in (STATE_GHOST, STATE_GHOST_ATK):
                        P2.start_kick()

                elif e.key == pg.K_KP6:
                    if P2.beast_active:
                        P2.start_beast_I()
                    else:
                        P2.start_combo()

                elif e.key == pg.K_UP:
                    P2.jump()


                elif e.key == pg.K_s:
                    P1.start_block()
                elif e.key == pg.K_DOWN:
                    P2.start_block()

            elif e.type == pg.KEYUP:
                if e.key == pg.K_s:       P1.stop_block()
                if e.key == pg.K_DOWN:    P2.stop_block()

        keys = pg.key.get_pressed()


        f1 = P1.current_frame()
        f2 = P2.current_frame()
        if not f1 or not f2:
            pg.display.flip()
            continue
        f1w, f1h = f1.get_size()
        f2w, f2h = f2.get_size()
        P1.prev_bottom = P1.y + f1h
        P2.prev_bottom = P2.y + f2h


        if P1.state not in (STATE_ATK, STATE_BLOCK, STATE_HIT, STATE_GHOST, STATE_GHOST_ATK, STATE_BEAST_ATK):
            p1_move = (1 if keys[pg.K_d] else 0) - (1 if keys[pg.K_a] else 0)
            if p1_move:
                speed = MOVE_SPEED * (BEAST_SPEED_MULT if P1.beast_active else 1.0)
                P1.x += p1_move * speed * dt
                P1.facing = 1 if p1_move > 0 else -1
                P1.set_walk(True)
            else:
                P1.set_walk(False)

        if P2.state not in (STATE_ATK, STATE_BLOCK, STATE_HIT, STATE_GHOST, STATE_GHOST_ATK, STATE_BEAST_ATK):
            p2_move = (1 if keys[pg.K_RIGHT] else 0) - (1 if keys[pg.K_LEFT] else 0)
            if p2_move:
                speed = MOVE_SPEED * (BEAST_SPEED_MULT if P2.beast_active else 1.0)
                P2.x += p2_move * speed * dt
                P2.facing = 1 if p2_move > 0 else -1
                P2.set_walk(True)
            else:
                P2.set_walk(False)


        P1.x = clamp_draw_x(P1.x, f1w, WIN_W, CLAMP_MARGIN)
        P2.x = clamp_draw_x(P2.x, f2w, WIN_W, CLAMP_MARGIN)


        if P1.state not in (STATE_GHOST, STATE_GHOST_ATK) and not P1.grounded:
            P1.vy += GRAVITY_PX_S2 * dt
            P1.y += P1.vy * dt
        if P2.state not in (STATE_GHOST, STATE_GHOST_ATK) and not P2.grounded:
            P2.vy += GRAVITY_PX_S2 * dt
            P2.y += P2.vy * dt


        def land_if_possible(F, fw, fh):
            if F.state in (STATE_GHOST, STATE_GHOST_ATK):
                return

            gy = fighter_landing_y(F, fw, fh)
            if gy is not None and F.vy >= 0 and F.y + fh >= gy:
                F.y = gy - fh
                F.vy = 0.0
                if not F.grounded:
                    F.grounded = True
                    if F.state not in (STATE_ATK, STATE_BLOCK, STATE_HIT, STATE_BEAST_ATK):
                        F.state = (STATE_BEAST if F.beast_active else STATE_IDLE)
                        F.anim = (F.beast_idle_clip if F.beast_active else F.idle_clip)
                        F.anim.reset()
            else:

                support_now = (gy is not None) and (abs((F.y + fh) - gy) <= 1.0)
                if not support_now:
                    if F.grounded:
                        F.grounded = False
                        if F.state not in (STATE_ATK, STATE_BLOCK, STATE_HIT, STATE_BEAST_ATK):
                            F.state = STATE_AIR
                            F.anim = (F.beast_idle_clip if F.beast_active else F.idle_clip)
                            F.anim.reset()

        land_if_possible(P1, f1w, f1h)
        land_if_possible(P2, f2w, f2h)


        P1.update(dt, ghost_floor_func=ghost_floor_y_under, fw=f1w, fh=f1h, is_p1=True)
        P2.update(dt, ghost_floor_func=ghost_floor_y_under, fw=f2w, fh=f2h, is_p1=False)

        # Fireball
        next_fb_in -= dt
        if next_fb_in <= 0.0:
            from_left = rnd.random() < 0.5
            vx = FIREBALL_SPEED if from_left else -FIREBALL_SPEED
            x = -80 if from_left else WIN_W + 20
            y_min = 120
            y_max = max(160, int(block_y - 160))
            y = rnd.randint(y_min, y_max)
            fireballs.append(Fireball(fireball_frames, x, y, vx))
            next_fb_in = rnd.uniform(FIREBALL_SPAWN_MIN, FIREBALL_SPAWN_MAX)

        for fb in fireballs:
            fb.update(dt)
            if fb.alive and fb.rect().colliderect(P1.bbox()):
                apply_damage(None, P1, FIREBALL_DAMAGE)
                fb.alive = False
            if fb.alive and fb.rect().colliderect(P2.bbox()):
                apply_damage(None, P2, FIREBALL_DAMAGE)
                fb.alive = False

        fireballs = [fb for fb in fireballs if fb.alive]


        p1_hitbox = P1.attack_hitbox()
        p2_hitbox = P2.attack_hitbox()

        # P1 -> P2
        if p1_hitbox and p1_hitbox.colliderect(P2.bbox()):
            if P1.state == STATE_GHOST_ATK and not P1.hit_registered:
                if P2.state in (STATE_GHOST, STATE_GHOST_ATK):
                    P2.end_ghost()
                P2.vuln_timer = GHOST_ATK_VULN_SECS
                P1.hit_registered = True
            else:
                atk_name, stage = P1.current_attack_stage()
                if atk_name == "beast_i" and not P1.hit_registered:
                    P2.blocking = False
                    apply_damage(P1, P2, DMG_BEAST_I, hit_flag=True)
                    P1.aura_timer = 0.35
                elif atk_name == "beast_sp" and not P1.hit_registered:
                    P2.blocking = False
                    apply_damage(P1, P2, DMG_BEAST_SP, hit_flag=True)
                elif atk_name == "beast_atk" and not P1.hit_registered:
                    apply_damage(P1, P2, DMG_BEAST_ATK, hit_flag=True)
                elif atk_name == "punch" and not P1.hit_registered and not P1.beast_active:
                    apply_damage(P1, P2, DMG_PUNCH, hit_flag=True)
                elif atk_name == "kick" and not P1.hit_registered and not P1.beast_active:
                    apply_damage(P1, P2, DMG_KICK, hit_flag=True)
                elif atk_name == "combo" and stage is not None and stage not in P1.combo_stages_hit:
                    apply_damage(P1, P2, DMG_COMBO[stage], combo_stage=stage)

        # P2 -> P1
        if p2_hitbox and p2_hitbox.colliderect(P1.bbox()):
            if P2.state == STATE_GHOST_ATK and not P2.hit_registered:
                if P1.state in (STATE_GHOST, STATE_GHOST_ATK):
                    P1.end_ghost()
                P1.vuln_timer = GHOST_ATK_VULN_SECS
                P2.hit_registered = True
            else:
                atk_name, stage = P2.current_attack_stage()
                if atk_name == "beast_i" and not P2.hit_registered:
                    P1.blocking = False
                    apply_damage(P2, P1, DMG_BEAST_I, hit_flag=True)
                    P2.aura_timer = 0.35
                elif atk_name == "beast_atk" and not P2.hit_registered:
                    apply_damage(P2, P1, DMG_BEAST_ATK, hit_flag=True)
                elif atk_name == "punch" and not P2.hit_registered and not P2.beast_active:
                    apply_damage(P2, P1, DMG_PUNCH, hit_flag=True)
                elif atk_name == "kick" and not P2.hit_registered and not P2.beast_active:
                    apply_damage(P2, P1, DMG_KICK, hit_flag=True)
                elif atk_name == "combo" and stage is not None and stage not in P2.combo_stages_hit:
                    apply_damage(P2, P1, DMG_COMBO[stage], combo_stage=stage)

        if p1_hp <= 0.0 or p2_hp <= 0.0:
            winner_text = "PLAYER 2 WINS" if p1_hp <= 0.0 else "PLAYER 1 WINS"
            show_winner_screen(screen, winner_text)
            reset_match()
            continue

        screen.blit(sky, (0, 0))
        screen.blit(sun, (WIN_W - sun.get_width() - 150, 80))


        screen.blit(block, block1_pos)
        screen.blit(block, block2_pos)

        screen.blit(small_block, small1_pos)
        screen.blit(small_block, small2_pos)


        for fb in fireballs:
            fb.draw(screen)

        blit_faced(screen, P1.current_frame(), (int(P1.x), int(P1.y)), P1.facing)
        blit_faced(screen, P2.current_frame(), (int(P2.x), int(P2.y)), P2.facing)

        if DEBUG_HITBOXES:
            if p1_hitbox: pg.draw.rect(screen, (0, 255, 0), p1_hitbox, 2)
            if p2_hitbox: pg.draw.rect(screen, (255, 0, 0), p2_hitbox, 2)
            pg.draw.rect(screen, (0, 200, 255), P1.bbox(), 1)
            pg.draw.rect(screen, (255, 180, 0), P2.bbox(), 1)
            # Platform debug
            pg.draw.rect(screen, (0, 180, 255), small1_rect, 1)
            pg.draw.rect(screen, (0, 180, 255), small2_rect, 1)
            pg.draw.line(screen, (255, 255, 0), (0, floor_top), (WIN_W, floor_top), 1)


        def draw_aura(surf, fighter: Fighter):
            if fighter.aura_timer <= 0.0: return
            alpha = max(0, min(200, int(200 * (fighter.aura_timer / 0.35))))
            cx, cy = fighter.bbox().center
            radius = fighter.bbox().height // 2 + 18
            aura = pg.Surface((radius * 2 + 4, radius * 2 + 4), pg.SRCALPHA)
            pg.draw.circle(aura, (255, 200, 80, alpha), (radius + 2, radius + 2), radius, width=6)
            surf.blit(aura, (cx - radius - 2, cy - radius - 2))

        draw_aura(screen, P1)
        draw_aura(screen, P2)


        bar_margin = 20
        bar_w, bar_h = 420, 32
        draw_health_and_meter(screen, bar_margin, bar_margin, bar_w, bar_h, p1_hp, P1.meter, P1_COLOR, "P1", font)
        draw_health_and_meter(screen, WIN_W - bar_margin - bar_w, bar_margin, bar_w, bar_h, p2_hp, P2.meter, P2_COLOR,
                              "P2", font)

        pg.display.flip()

    pg.quit()


if __name__ == "__main__":
    main()
