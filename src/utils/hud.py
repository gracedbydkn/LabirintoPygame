import pygame
from src.world.entities.item import Item


# ---------------------------------------------------------------------------
# Carregamento de teclas
# ---------------------------------------------------------------------------

def carregar_tecla(nome, tamanho=(40, 40)):
    try:
        raw = pygame.image.load(f"assets/keyboard-keys/{nome}.png").convert_alpha()
        rw, rh = raw.get_size()
        fw = rw // 3
        return [
            pygame.transform.scale(raw.subsurface((i * fw, 0, fw, rh)), tamanho)
            for i in range(3)
        ]
    except (FileNotFoundError, pygame.error):
        return None


def carregar_teclas():
    nomes = ["E", "W", "A", "S", "D", "ARROWUP", "ARROWLEFT", "ARROWDOWN", "ARROWRIGHT", "SHIFTBIGGER"]
    return {n: carregar_tecla(n) for n in nomes}


# ---------------------------------------------------------------------------
# Carregamento dos assets de HUD
# ---------------------------------------------------------------------------

def carregar_assets_hud():
    assets = {}
    try:
        assets["portrait_frame"] = pygame.image.load("assets/itens/portrait_frame.png").convert_alpha()
    except (FileNotFoundError, pygame.error):
        assets["portrait_frame"] = None
    return assets


# ---------------------------------------------------------------------------
# Dicas de teclas
# ---------------------------------------------------------------------------

def draw_key_hints(screen, player, world_objects, items, key_hints, camera, time):
    ciclo = time % 0.86
    f = 0 if ciclo < 0.50 else (1 if ciclo < 0.68 else 2)

    alvo = player._get_objeto_proximo(world_objects, items)
    pode_interagir = (
        alvo and (
            (isinstance(alvo, Item) and not alvo.dead)
            or (hasattr(alvo, 'interactable') and alvo.interactable and alvo.interactable.enabled)
        )
    )
    if not pode_interagir:
        alvo = player._get_objeto_proximo([], items)
        pode_interagir = bool(alvo)

    frames = pode_interagir and key_hints.get("E")
    if frames:
        sx = int(alvo.x - camera.x)
        sy = int(alvo.y - camera.y) - 100
        frame = frames[f]
        screen.blit(frame, (sx - frame.get_width() // 2, sy - frame.get_height() // 2))

    if player.idle_time >= 5.0 and not player.is_hidden:
        sw, sh = screen.get_size()
        setas = int(player.idle_time / 3.5) % 2 == 1
        step = 44
        cx, cy = sw // 2, sh - 72
        teclas = (
            [("ARROWUP", cx, cy - step), ("ARROWLEFT", cx - step, cy),
             ("ARROWDOWN", cx, cy), ("ARROWRIGHT", cx + step, cy)]
            if setas else
            [("W", cx, cy - step), ("A", cx - step, cy),
             ("S", cx, cy), ("D", cx + step, cy)]
        )
        for nome, x, y in teclas:
            frames = key_hints.get(nome)
            if frames:
                frame = frames[f]
                screen.blit(frame, (x - frame.get_width() // 2, y - frame.get_height() // 2))

        shift_frames = key_hints.get("SHIFTBIGGER")
        if shift_frames:
            shift_frame = shift_frames[f]
            shift_x = cx - int(step * 2.5)
            screen.blit(shift_frame, (shift_x - shift_frame.get_width() // 2, cy - shift_frame.get_height() // 2))


# ---------------------------------------------------------------------------
# Overlay de game over / vitória
# ---------------------------------------------------------------------------

def draw_ui_overlay(screen, font_lg, font_sm, title, color, bg_color, hud_text_color):
    sw, sh = screen.get_size()
    ov = pygame.Surface((sw, sh), pygame.SRCALPHA)
    ov.fill(bg_color)
    screen.blit(ov, (0, 0))
    txt_title = font_lg.render(title, True, color)
    txt_sub   = font_sm.render("R = Tentar Novamente  •  ESC = Sair", True, hud_text_color)
    screen.blit(txt_title, txt_title.get_rect(center=(sw // 2, sh // 2 - 20)))
    screen.blit(txt_sub,   txt_sub.get_rect(center=(sw // 2, sh // 2 + 30)))


# ---------------------------------------------------------------------------
# HUD principal
# ---------------------------------------------------------------------------

def draw_hud(screen, clock, player, font_sm, env_frames, hud_assets):
    sw, sh = screen.get_size()
    margin = 16

    # ── Barra de Stamina ────────────────────────────────────────────────────
    if player.is_running or player.stamina < player.max_stamina:
        bar_w = 150  # Largura da barra
        bar_h = 13   # Altura (bem fina e minimalista)
        
        # Centraliza a barra horizontalmente e a posiciona perto do fundo da tela
        bar_x = (sw - bar_w) // 2
        bar_y = sh - margin - 80
        
        stamina_pct = player.stamina / player.max_stamina
        fill_w = int(stamina_pct * bar_w)
        
        # 1. Fundo da barra
        pygame.draw.rect(screen, (30, 30, 30), (bar_x, bar_y, bar_w, bar_h))
        
        # 2. Preenchimento da barra
        if fill_w > 0:
            # Fica vermelha se o jogador esgotar o fôlego, senão fica branca
            cor_fill = (200, 50, 50) if player.exhausted else (240, 240, 240)
            pygame.draw.rect(screen, cor_fill, (bar_x, bar_y, fill_w, bar_h))
            
        # 3. Borda preta fina para destacar em fundos claros
        pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_w, bar_h), 1)

    # FPS abaixo da barra
    fps = int(clock.get_fps())
    cor = (100, 220, 100) if fps >= 55 else (255, 200, 0) if fps >= 30 else (255, 80, 80)
    screen.blit(font_sm.render(f"FPS: {fps}", True, cor), (margin, margin))

    # ── Inventário com portrait_frame ────────────────────────────────────────
    inventario = player.inventory.listar()
    if not inventario:
        return

    portrait_img = hud_assets.get("portrait_frame")

    # asset original: 48x72 — escala 2×
    SLOT_SCALE = 2
    SLOT_SW    = 48 * SLOT_SCALE   # 96
    SLOT_SH    = 72 * SLOT_SCALE   # 144
    SLOT_PAD   = 8
    ICON_SIZE  = int(SLOT_SW * 0.50)

    hud_x = margin
    hud_y = sh - margin - SLOT_SH - 20   # 20 px para o label abaixo

    for i, item in enumerate(inventario):
        sx = hud_x + i * (SLOT_SW + SLOT_PAD)
        sy = hud_y

        # Fundo escuro
        bg = pygame.Surface((SLOT_SW, SLOT_SH), pygame.SRCALPHA)
        bg.fill((15, 10, 20, 210))
        screen.blit(bg, (sx, sy))

        # Ícone centralizado
        frames = env_frames.get(item.item_type)
        if frames:
            raw_frame = frames[0]
            if isinstance(raw_frame, list):
                raw_frame = raw_frame[0]
            icon = pygame.transform.smoothscale(raw_frame, (ICON_SIZE, ICON_SIZE))
            screen.blit(icon, (
                sx + (SLOT_SW - ICON_SIZE) // 2,
                sy + (SLOT_SH - ICON_SIZE) // 2,
            ))

        # Frame por cima
        if portrait_img:
            frame_scaled = pygame.transform.scale(portrait_img, (SLOT_SW, SLOT_SH))
            screen.blit(frame_scaled, (sx, sy))

        # Label abaixo
        nome  = "Chave" if item.item_type == "chave" else "Runa"
        label = font_sm.render(nome, True, (220, 200, 150))
        screen.blit(label, (sx + (SLOT_SW - label.get_width()) // 2, sy + SLOT_SH + 2))