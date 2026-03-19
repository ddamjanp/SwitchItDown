import pygame as pg

from settings import START_IMG_PATH, WIN_W, WIN_H


def show_start_screen(screen, win_w, win_h):
    img = pg.image.load(START_IMG_PATH).convert_alpha()
    bg_color = img.get_at((0, 0))[:3]

    scale_factor = 6
    big = pg.transform.smoothscale(
        img,
        (img.get_width() * scale_factor, img.get_height() * scale_factor)
    )

    title_font = pg.font.SysFont("consolas", 48, bold=True)
    hint_font = pg.font.SysFont("consolas", 28)

    title = title_font.render("Press SPACE to Start", True, (255, 255, 255))
    hint = hint_font.render("ESC to Quit", True, (230, 230, 230))

    clock = pg.time.Clock()
    waiting = True

    while waiting:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                raise SystemExit
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    pg.quit()
                    raise SystemExit
                if e.key == pg.K_SPACE:
                    waiting = False

        screen.fill(bg_color)

        bx = (win_w - big.get_width()) // 2
        by = (win_h - big.get_height()) // 2 - 40
        screen.blit(big, (bx, by))

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
                pg.quit()
                raise SystemExit
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    pg.quit()
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