# src/world/fog.py
import pygame
import math
from src.core.config import *

class FogOfWar:
    def __init__(self):
        self._grad_cache = {}

    def _cast_ray(self, ox, oy, angle, max_dist):
        dx = math.cos(angle)
        dy = math.sin(angle)
        step = 4
        dist = 0.0
        while dist < max_dist:
            dist += step
            tx = int((ox + dx * dist) // TILE)
            ty = int((oy + dy * dist) // TILE)
            if tx < 0 or ty < 0 or tx >= MAP_COLS or ty >= MAP_ROWS:
                return dist
            if MAZE_DATA[ty][tx] == 1:
                return dist
        return max_dist

    def _get_gradient(self, radius):
        if radius in self._grad_cache:
            return self._grad_cache[radius]
        size = radius * 2 + 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        c = radius + 1
        for r in range(radius, 0, -1):
            ratio = r / radius
            t = ratio * ratio * (3 - 2 * ratio)
            alpha = int(255 * t)
            pygame.draw.circle(surf, (0, 0, 0, alpha), (c, c), r)
        self._grad_cache[radius] = surf
        return surf

    def draw(self, surface, player_x, player_y, camera, time):
        w, h = surface.get_size()
        fog = pygame.Surface((w, h), pygame.SRCALPHA)
        fog.fill((0, 0, 0, 240))

        cx = player_x - camera.x
        cy = player_y - camera.y
        max_r = FOV_RADIUS + FOV_SOFT_EDGE
        
        pts = []
        for i in range(FOV_RAYS):
            angle = (i / FOV_RAYS) * math.tau
            dist = self._cast_ray(player_x, player_y, angle, max_r)
            pts.append((int(cx + math.cos(angle) * dist), int(cy + math.sin(angle) * dist)))
            
        if len(pts) >= 3:
            pygame.draw.polygon(fog, (0, 0, 0, 0), pts)

        grad = self._get_gradient(FOV_RADIUS + FOV_SOFT_EDGE)
        fog.blit(grad, grad.get_rect(center=(int(cx), int(cy))), special_flags=pygame.BLEND_RGBA_MAX)

        flicker = int(3 * math.sin(time * 7.3) + 2 * math.sin(time * 13.1))
        fog.set_alpha(max(0, min(255, 225 + flicker)))

        surface.blit(fog, (0, 0))