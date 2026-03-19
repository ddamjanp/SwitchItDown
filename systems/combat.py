from settings import (
    STATE_GHOST,
    STATE_GHOST_ATK,
    BLOCK_MULTIPLIER,
    BEAST_DMG_MULT,
)

# Global HP (same behavior as your original code)
p1_hp = 1.0
p2_hp = 1.0


def apply_damage(attacker, defender, base_dmg, hit_flag=False, combo_stage=None):
    global p1_hp, p2_hp

    # Ghosts cannot be damaged
    if defender.state in (STATE_GHOST, STATE_GHOST_ATK):
        return

    dmg = base_dmg

    # Blocking reduces damage
    if defender.blocking:
        dmg *= BLOCK_MULTIPLIER

    # Beast attacker bonus
    if attacker is not None and attacker.beast_active:
        dmg *= BEAST_DMG_MULT

    # Vulnerability multiplier
    if attacker is not None and attacker.state not in (STATE_GHOST, STATE_GHOST_ATK):
        dmg *= defender.vuln_mult()

    # Apply damage to correct player
    if defender.name == "P1":
        p1_hp = max(0.0, p1_hp - dmg)
    else:
        p2_hp = max(0.0, p2_hp - dmg)

    # Mark hits
    if attacker is not None and hit_flag:
        attacker.hit_registered = True

    if attacker is not None and combo_stage is not None:
        attacker.combo_stages_hit.add(combo_stage)

    # Trigger hit animation if not blocking
    if not defender.blocking and dmg > 0:
        defender.start_hit()