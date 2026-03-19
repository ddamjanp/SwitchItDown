import random as rnd

import pygame as pg

from settings import *
from assets import (
    load_environment,
    load_fighter_frames,
    build_fighter_clips,
    load_ghost_clips,
    load_beast_clips_p1,
    load_beast_clips_p2,
    load_fireball_frames,
)
from animations import blit_faced, clamp_draw_x
from entities.fighter import Fighter
from entities.fireball import Fireball
from systems import combat
from systems.world import ghost_floor_y_under, fighter_landing_y, land_if_possible
from ui.hud import draw_health_and_meter, draw_aura
from ui.screens import show_start_screen, show_winner_screen


def main():
    pg.init()
    screen = pg.display.set_mode((WIN_W, WIN_H))
    pg.display.set_caption("Switch it down")
    show_start_screen(screen, WIN_W, WIN_H)

    sky, sun, block = load_environment()

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

    frames1, frames2 = load_fighter_frames()

    p1_idle, p1_walk, p1_punch, p1_kick, p1_block, p1_combo, p1_hit = build_fighter_clips(frames1)
    p2_idle, p2_walk, p2_punch, p2_kick, p2_block, p2_combo, p2_hit = build_fighter_clips(frames2)

    ghost_idle_clip, ghost_transform_clip, ghost_attack_clip = load_ghost_clips()

    (
        beast_idle_clip,
        beast_walk_clip,
        beast_transform_clip,
        beast_attack_clip,
        beast_special_clip,
        beast_i_clip,
        beast_hit_clip,
    ) = load_beast_clips_p1()

    (
        p2_beast_idle_clip,
        p2_beast_walk_clip,
        p2_beast_transform_clip,
        p2_beast_attack_clip,
        p2_beast_i_clip,
        p2_beast_hit_clip,
    ) = load_beast_clips_p2()

    fw1_0, fh1_0 = p1_idle.get().get_size()
    fw2_0, fh2_0 = p2_idle.get().get_size()
    p1_start_x = block1_pos[0] + block.get_width() // 2 - fw1_0 // 2
    p2_start_x = block2_pos[0] + block.get_width() // 2 - fw2_0 // 2

    combat.p1_hp = 1.0
    combat.p2_hp = 1.0

    P1 = Fighter(
        frames1,
        p1_idle,
        p1_walk,
        p1_punch,
        p1_kick,
        p1_block,
        p1_combo,
        p1_hit,
        ghost_idle_clip,
        ghost_transform_clip,
        ghost_attack_clip,
        beast_idle_clip,
        beast_walk_clip,
        beast_transform_clip,
        beast_attack_clip,
        beast_special_clip,
        beast_i_clip,
        beast_hit_clip,
        p1_start_x,
        0,
        facing=1,
        name="P1",
    )

    P2 = Fighter(
        frames2,
        p2_idle,
        p2_walk,
        p2_punch,
        p2_kick,
        p2_block,
        p2_combo,
        p2_hit,
        ghost_idle_clip,
        ghost_transform_clip,
        ghost_attack_clip,
        p2_beast_idle_clip,
        p2_beast_walk_clip,
        p2_beast_transform_clip,
        p2_beast_attack_clip,
        None,
        p2_beast_i_clip,
        p2_beast_hit_clip,
        p2_start_x,
        0,
        facing=-1,
        name="P2",
    )

    fireball_frames = load_fireball_frames()

    fireballs = []
    next_fb_in = rnd.uniform(FIREBALL_SPAWN_MIN, FIREBALL_SPAWN_MAX)

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
        nonlocal fireballs, next_fb_in

        combat.p1_hp = 1.0
        combat.p2_hp = 1.0

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

                elif e.key == pg.K_k:
                    P1.toggle_ghost()
                elif e.key == pg.K_KP3:
                    P2.toggle_ghost()
                elif e.key == pg.K_j:
                    P1.toggle_beast()
                elif e.key == pg.K_KP1:
                    P2.toggle_beast()

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
                if e.key == pg.K_s:
                    P1.stop_block()
                if e.key == pg.K_DOWN:
                    P2.stop_block()

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

        land_if_possible(
            P1,
            f1w,
            f1h,
            fighter_landing_y,
            block1_rect,
            block2_rect,
            small1_rect,
            small2_rect,
        )
        land_if_possible(
            P2,
            f2w,
            f2h,
            fighter_landing_y,
            block1_rect,
            block2_rect,
            small1_rect,
            small2_rect,
        )

        P1.update(dt, ghost_floor_func=ghost_floor_y_under(floor_top), fw=f1w, fh=f1h, is_p1=True)
        P2.update(dt, ghost_floor_func=ghost_floor_y_under(floor_top), fw=f2w, fh=f2h, is_p1=False)

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
                combat.apply_damage(None, P1, FIREBALL_DAMAGE)
                fb.alive = False
            if fb.alive and fb.rect().colliderect(P2.bbox()):
                combat.apply_damage(None, P2, FIREBALL_DAMAGE)
                fb.alive = False

        fireballs = [fb for fb in fireballs if fb.alive]

        p1_hitbox = P1.attack_hitbox()
        p2_hitbox = P2.attack_hitbox()

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
                    combat.apply_damage(P1, P2, DMG_BEAST_I, hit_flag=True)
                    P1.aura_timer = 0.35
                elif atk_name == "beast_sp" and not P1.hit_registered:
                    P2.blocking = False
                    combat.apply_damage(P1, P2, DMG_BEAST_SP, hit_flag=True)
                elif atk_name == "beast_atk" and not P1.hit_registered:
                    combat.apply_damage(P1, P2, DMG_BEAST_ATK, hit_flag=True)
                elif atk_name == "punch" and not P1.hit_registered and not P1.beast_active:
                    combat.apply_damage(P1, P2, DMG_PUNCH, hit_flag=True)
                elif atk_name == "kick" and not P1.hit_registered and not P1.beast_active:
                    combat.apply_damage(P1, P2, DMG_KICK, hit_flag=True)
                elif atk_name == "combo" and stage is not None and stage not in P1.combo_stages_hit:
                    combat.apply_damage(P1, P2, DMG_COMBO[stage], combo_stage=stage)

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
                    combat.apply_damage(P2, P1, DMG_BEAST_I, hit_flag=True)
                    P2.aura_timer = 0.35
                elif atk_name == "beast_atk" and not P2.hit_registered:
                    combat.apply_damage(P2, P1, DMG_BEAST_ATK, hit_flag=True)
                elif atk_name == "punch" and not P2.hit_registered and not P2.beast_active:
                    combat.apply_damage(P2, P1, DMG_PUNCH, hit_flag=True)
                elif atk_name == "kick" and not P2.hit_registered and not P2.beast_active:
                    combat.apply_damage(P2, P1, DMG_KICK, hit_flag=True)
                elif atk_name == "combo" and stage is not None and stage not in P2.combo_stages_hit:
                    combat.apply_damage(P2, P1, DMG_COMBO[stage], combo_stage=stage)

        if combat.p1_hp <= 0.0 or combat.p2_hp <= 0.0:
            winner_text = "PLAYER 2 WINS" if combat.p1_hp <= 0.0 else "PLAYER 1 WINS"
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
            if p1_hitbox:
                pg.draw.rect(screen, (0, 255, 0), p1_hitbox, 2)
            if p2_hitbox:
                pg.draw.rect(screen, (255, 0, 0), p2_hitbox, 2)
            pg.draw.rect(screen, (0, 200, 255), P1.bbox(), 1)
            pg.draw.rect(screen, (255, 180, 0), P2.bbox(), 1)
            pg.draw.rect(screen, (0, 180, 255), small1_rect, 1)
            pg.draw.rect(screen, (0, 180, 255), small2_rect, 1)
            pg.draw.line(screen, (255, 255, 0), (0, floor_top), (WIN_W, floor_top), 1)

        draw_aura(screen, P1)
        draw_aura(screen, P2)

        bar_margin = 20
        bar_w, bar_h = 420, 32
        draw_health_and_meter(screen, bar_margin, bar_margin, bar_w, bar_h, combat.p1_hp, P1.meter, P1_COLOR, "P1",
                              font)
        draw_health_and_meter(
            screen,
            WIN_W - bar_margin - bar_w,
            bar_margin,
            bar_w,
            bar_h,
            combat.p2_hp,
            P2.meter,
            P2_COLOR,
            "P2",
            font,
        )

        pg.display.flip()

    pg.quit()
