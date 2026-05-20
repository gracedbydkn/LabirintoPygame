# src/core/config.py
import pygame

# Resolução inicial da janela do jogo
INIT_SCREEN_W, INIT_SCREEN_H = 800, 600

# Limite de frames por segundo — controla a velocidade do loop principal
FPS = 60

# --- Configurações de Visão (Fog of War) ---

# Raio em pixels da área iluminada ao redor do jogador
FOV_RADIUS = 280

# Número de raios lançados para calcular o campo de visão (um por grau = 360°)
FOV_RAYS = 360

# Zona extra além do FOV_RADIUS onde a luz se apaga gradualmente (evita corte abrupto)
FOV_SOFT_EDGE = 120

# --- Paleta de Cores Dark Fantasy (valores RGB) ---

# Cor de fundo da tela — preto-roxo profundo
C_BG = (4, 3, 10)

# Tons de parede: do mais escuro (sombra) ao mais claro (borda iluminada)
C_WALL_DARK  = (15, 12, 25)
C_WALL_MID   = (40, 35, 65)
C_WALL_LIGHT = (65, 55, 100)
C_WALL_EDGE  = (85, 75, 130)

# Tons do chão: escuro base e pontilhado decorativo
C_FLOOR_DARK = (12, 10, 20)
C_FLOOR_MID  = (18, 15, 30)
C_FLOOR_DOT  = (25, 20, 40)

# Cor dos esconderijos (tiles onde o jogador pode se ocultar)
C_HIDE_SPOT = (8, 6, 15)

# Cor do brilho/aura ao redor do jogador
C_PLAYER_GLOW = (40, 120, 200)

# Cor da saída do labirinto e seu brilho (dourado)
C_EXIT      = (255, 215, 0)
C_EXIT_GLOW = (255, 180, 0)

# Cor do texto do HUD (interface) — lilás claro para combinar com o tema
C_HUD_TEXT = (200, 180, 255)