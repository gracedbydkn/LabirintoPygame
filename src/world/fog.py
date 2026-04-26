# src/world/fog.py
import pygame
import math
from src.core.config import *

class FogOfWar:
    def __init__(self):
        self._grad_cache = {}

    def _cast_ray(self, ox, oy, angle, max_dist, maze):
        dx = math.cos(angle)
        dy = math.sin(angle)
        step = 4
        dist = 0.0
        hit_wall = False

        while dist < max_dist:
            dist += step
            tx = int((ox + dx * dist) // maze.tile_size)
            ty = int((oy + dy * dist) // maze.tile_size)
            
            if tx < 0 or ty < 0 or tx >= maze.cols or ty >= maze.rows:
                return dist
            
            if maze.matrix[ty][tx] == 1:
                hit_wall = True
            else:
                if hit_wall:
                    return dist
        return max_dist

    def _get_gradient(self, radius):
        if radius in self._grad_cache:
            return self._grad_cache[radius]
        
        size = int(radius * 2)
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        center = int(radius)
        
        for r in range(int(radius), 0, -1):
            ratio = r / radius
            t = ratio * ratio * (3 - 2 * ratio)
            alpha = int(255 * (1 - t))
            pygame.draw.circle(surf, (255, 255, 255, alpha), (center, center), r)
            
        self._grad_cache[radius] = surf
        return surf

    def draw(self, surface, player_x, player_y, camera, time, maze):
        w, h = surface.get_size()
        
        fog = pygame.Surface((w, h), pygame.SRCALPHA)
        flicker = int(3 * math.sin(time * 7.3) + 2 * math.sin(time * 13.1))
        base_alpha = max(0, min(255, 240 + flicker))
        fog.fill((0, 0, 0, base_alpha))

        light_mask = pygame.Surface((w, h), pygame.SRCALPHA)
        light_mask.fill((0, 0, 0, 0))

        cx = player_x - camera.x
        cy = player_y - camera.y
        max_r = FOV_RADIUS + FOV_SOFT_EDGE
        
        pts = []
        for i in range(FOV_RAYS):
            angle = (i / FOV_RAYS) * math.tau
            dist = self._cast_ray(player_x, player_y, angle, max_r, maze)
            pts.append((int(cx + math.cos(angle) * dist), int(cy + math.sin(angle) * dist)))
            
        if len(pts) >= 3:
            pygame.draw.polygon(light_mask, (255, 255, 255, 255), pts)
        grad = self._get_gradient(max_r)
        light_mask.blit(grad, grad.get_rect(center=(int(cx), int(cy))), special_flags=pygame.BLEND_RGBA_MIN)
        fog.blit(light_mask, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        
        surface.blit(fog, (0, 0))