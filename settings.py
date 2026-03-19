# ---------- Window ----------
WIN_W, WIN_H = 1280, 720

# ---------- Asset Paths ----------
SKY_PATH = "graphics/back.png"
SUN_PATH = "graphics/cethiel-desert-edit-small-swm-version-layer3.png"
BLOCK_PATH = "graphics/brown platform merged transparent.png"
P1_SHEET = "graphics/fighter_base/cat_fighter_sprite1.png"
P2_SHEET = "graphics/fighter_base/cat_fighter_sprite2.png"
GHOST_SHEET = "graphics/ghost_base/mon3_sprite_base.png"
START_IMG_PATH = "graphics/cat_walk_shot.gif"

# Beast sheets
BEAST_SHEET = "graphics/p1_beast_base/mon2_sprite_base.png"
P2_BEAST_SHEET = "graphics/p2_beast_base/mon1_sprite_addon_2012_12_14.png"

# Fireball sheet
FIREBALL_SHEET = "graphics/energy_effect_base.png"

# ---------- Fighter Sprite Sheet ----------
FRAME_W, FRAME_H = 50, 50
SHEET_COLS = 10
TARGET_CHAR_H = 110

# Animation ranges
IDLE_START_INDEX = 5
IDLE_FRAME_COUNT = 2
WALK_START_INDEX = 3
WALK_FRAME_COUNT = 2

# Animation indices (precomputed from rc_to_indices)
PUNCH_IDX = [37, 38, 39]
KICK_IDX = [6, 7, 8, 9]
BLOCK_IDX = [50, 51]
COMBO_IDX = [40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 54, 55, 56, 57, 58, 59]
HIT_IDX = [0, 1, 2]

# ---------- Ghost Sprite Sheet ----------
GHOST_FRAME_W = 64
GHOST_FRAME_H = 64

# ---------- Beast Sprite Sheet ----------
BEAST_FRAME_W = 64
BEAST_FRAME_H = 64

# ---------- Movement ----------
MOVE_SPEED = 360.0
CLAMP_MARGIN = 10

# ---------- Physics ----------
GRAVITY_PX_S2 = 2600.0
JUMP_VELOCITY = -900.0

# ---------- Damage ----------
DMG_PUNCH = 0.04
DMG_KICK = 0.048
DMG_COMBO = [0.05, 0.10, 0.10, 0.05]
BLOCK_MULTIPLIER = 0.1

# Beast modifiers
BEAST_DMG_MULT = 1.25
BEAST_SPEED_MULT = 1.35

# Beast attacks
DMG_BEAST_ATK = 0.06
DMG_BEAST_SP = 0.08
DMG_BEAST_I = 0.10

# ---------- Hitboxes ----------
HITBOX_DEPTH = 30
HITBOX_INSET_Y = 20
DEBUG_HITBOXES = False

# ---------- Colors ----------
P1_COLOR = (90, 200, 255)
P2_COLOR = (255, 160, 80)
UI_WHITE = (245, 245, 245)

# ---------- Ground ----------
GROUND_DROP = 80
FEET_OFFSET = 82

# ---------- Meter ----------
METER_GAIN_RATE = 0.10
METER_COST_COMBO = 1.0 / 3.0

# ---------- Ghost ----------
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

# ---------- Beast States ----------
STATE_BEAST = "BEAST"
STATE_BEAST_ATK = "BEAST_ATK"

# ---------- General States ----------
STATE_IDLE = "IDLE"
STATE_WALK = "WALK"
STATE_ATK = "ATTACK"
STATE_AIR = "AIR"
STATE_BLOCK = "BLOCK"
STATE_HIT = "HIT"

# ---------- Fireball ----------
FIREBALL_FRAME_W = 32
FIREBALL_FRAME_H = 32
FIREBALL_SPEED = 420.0
FIREBALL_DAMAGE = 0.06
FIREBALL_SPAWN_MIN = 1.6
FIREBALL_SPAWN_MAX = 3.2