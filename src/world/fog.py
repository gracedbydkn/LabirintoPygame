# src/world/fog.py
import pygame
import math
from src.core.config import *

class FogOfWar:
    def __init__(self):
        # Cache para superfícies de gradiente já geradas — evita recriar a cada frame
        self._grad_cache = {}

    def _get_gradient(self, radius):
        """Cria (ou recupera do cache) uma superfície circular com transparência gradual.
        O centro é totalmente transparente e as bordas são opacas — simula a queda de luz."""
        if radius in self._grad_cache:
            return self._grad_cache[radius]

        size = int(radius * 2)
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))  # Começa totalmente transparente
        center = int(radius)

        # Desenha círculos concêntricos do maior para o menor, com alpha crescente nas bordas
        for r in range(int(radius), 0, -1):
            ratio = r / radius
            # Curva smoothstep: transição suave sem ser linear
            t = ratio * ratio * (3 - 2 * ratio)
            alpha = int(255 * (1 - t))  # Centro transparente → borda opaca
            pygame.draw.circle(surf, (255, 255, 255, alpha), (center, center), r)

        # Armazena no cache para reutilizar nos próximos frames
        self._grad_cache[radius] = surf
        return surf
    
    def _get_torch_glow(self, radius):
        """Gradiente de calor da tocha."""
        key = ('glow', radius)
        if key in self._grad_cache:
            return self._grad_cache[key]

        size = int(radius * 2)
        surf = pygame.Surface((size, size)) 
        surf.fill((0, 0, 0))
        center = int(radius)

        for r in range(int(radius), 0, -1):
            ratio = r / radius
            t = ratio * ratio * (3 - 2 * ratio)
            b = 1 - t
            pygame.draw.circle(surf, (int(160*b), int(90*b), int(20*b)), (center, center), r)

        self._grad_cache[key] = surf
        return surf

    def draw(self, surface, player_x, player_y, camera, time, maze, tochas=()):
        """Renderiza a névoa de guerra sobre a superfície principal.
        O processo: cobre tudo de preto → abre um buraco onde o jogador enxerga."""
        w, h = surface.get_size()
        cx = player_x - camera.x
        cy = player_y - camera.y
        max_r = FOV_RADIUS + FOV_SOFT_EDGE
        grad = self._get_gradient(max_r)

        torch_r    = TORCH_FOV_RADIUS + TORCH_FOV_SOFT
        torch_grad = self._get_gradient(torch_r)
        torch_glow = self._get_torch_glow(torch_r)
        for tx, ty in tochas:
            tcx = int(tx - camera.x)
            tcy = int(ty - camera.y)
            phase = (tx * 0.031 + ty * 0.017) % (2 * math.pi)
            flicker_a = int(90 + 30 * math.sin(time * 6.1 + phase) + 20 * math.sin(time * 11.7 + phase))
            torch_glow.set_alpha(max(40, min(120, flicker_a)))
            surface.blit(torch_glow, torch_glow.get_rect(center=(tcx, tcy)), special_flags=pygame.BLEND_ADD)

        # Máscara 1: preto (para o inimigo não aparecer)
        fog1 = pygame.Surface((w, h), pygame.SRCALPHA)
        fog1.fill((0, 0, 0, 255))
        fog1.blit(grad, grad.get_rect(center=(int(cx), int(cy))), special_flags=pygame.BLEND_RGBA_SUB)
        for tx, ty in tochas:
            fog1.blit(torch_grad, torch_grad.get_rect(center=(int(tx - camera.x), int(ty - camera.y))), special_flags=pygame.BLEND_RGBA_SUB)
        surface.blit(fog1, (0, 0))

        # Máscara 2: a luz
        flicker = int(3 * math.sin(time * 7.3) + 2 * math.sin(time * 13.1))
        base_alpha = max(0, min(255, 240 + flicker))
        fog2 = pygame.Surface((w, h), pygame.SRCALPHA)
        fog2.fill((0, 0, 0, base_alpha))
        fog2.blit(grad, grad.get_rect(center=(int(cx), int(cy))), special_flags=pygame.BLEND_RGBA_SUB)
        for tx, ty in tochas: 
            fog2.blit(torch_grad, torch_grad.get_rect(center=(int(tx - camera.x), int(ty - camera.y))), special_flags=pygame.BLEND_RGBA_SUB)
        surface.blit(fog2, (0, 0))