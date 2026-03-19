import pygame as pg

from settings import UI_WHITE


def draw_bar(screen, x, y, w, h, pct, color, border_col=(10, 10, 15), bg_col=(50, 50, 60)):
    pct = max(0.0, min(1.0, pct))
    pg.draw.rect(screen, bg_col, (x, y, w, h), border_radius=8)
    pg.draw.rect(screen, color, (x + 3, y + 3, int((w - 6) * pct), h - 6), border_radius=8)
    pg.draw.rect(screen, border_col, (x, y, w, h), 2, border_radius=8)


def draw_health_and_meter(screen, x, y, w, h, hp, meter, color, label, font):
    draw_bar(screen, x, y, w, h, hp, color)
    screen.blit(font.render(label, True, UI_WHITE), (x, y - 20))
    draw_bar(screen, x, y + h + 6, w, int(h * 0.6), meter, (180, 120, 255))


def draw_aura(surf, fighter):
    if fighter.aura_timer <= 0.0:
        return

    alpha = max(0, min(200, int(200 * (fighter.aura_timer / 0.35))))
    cx, cy = fighter.bbox().center
    radius = fighter.bbox().height // 2 + 18

    aura = pg.Surface((radius * 2 + 4, radius * 2 + 4), pg.SRCALPHA)
    pg.draw.circle(aura, (255, 200, 80, alpha), (radius + 2, radius + 2), radius, width=6)
    surf.blit(aura, (cx - radius - 2, cy - radius - 2))