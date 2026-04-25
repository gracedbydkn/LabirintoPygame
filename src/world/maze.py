# src/world/maze.py
import pygame
import math
from src.core.config import *

class Maze:
    def __init__(self):
        self.data = MAZE_DATA
        self.wall_surf = self._make_wall_tile()
        self.floor_surf = self._make_floor_tile()
        self.hide_surf = self._make_hide_tile()
        self.exit_surf = self._make_exit_tile()
        
        self.wall_rects = []
        self.exit_rect = None
        
        for row in range(MAP_ROWS):
            for col in range(MAP_COLS):
                if self.data[row][col] == 1:
                    self.wall_rects.append(pygame.Rect(col*TILE, row*TILE, TILE, TILE))
                elif self.data[row][col] == 2:
                    self.exit_rect = pygame.Rect(col*TILE, row*TILE, TILE, TILE)

    def _make_wall_tile(self):
        surf = pygame.Surface((TILE, TILE))
        surf.fill(C_WALL_DARK)
        #pygame.draw.rect(surf, C_WALL_LIGHT, (2, 2, TILE-4, TILE-4), 1)
        #pygame.draw.line(surf, C_WALL_EDGE, (0, 0), (TILE-1, 0))
        #pygame.draw.line(surf, C_WALL_EDGE, (0, 0), (0, TILE-1))
        return surf

    def _make_floor_tile(self):
        surf = pygame.Surface((TILE, TILE))
        surf.fill(C_FLOOR_DARK)
        pygame.draw.circle(surf, C_FLOOR_DOT, (TILE//2, TILE//2), 1)
        return surf

    def _make_hide_tile(self):
        surf = pygame.Surface((TILE, TILE))
        surf.fill(C_HIDE_SPOT)
        # Padrão visual sutil para indicar esconderijo
        for i in range(0, TILE, 8):
            pygame.draw.line(surf, C_FLOOR_DARK, (0, i), (TILE, i), 1)
        return surf

    def _make_exit_tile(self):
        surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
        surf.fill((0,0,0,0))
        pygame.draw.rect(surf, (*C_EXIT, 200), (4, 4, TILE-8, TILE-8), border_radius=3)
        return surf

    def draw(self, surface, camera, time=0):
        cx, cy = int(camera.x), int(camera.y)
        sw, sh = surface.get_size()
        
        c0 = max(0, cx // TILE)
        r0 = max(0, cy // TILE)
        c1 = min(MAP_COLS, c0 + sw // TILE + 2)
        r1 = min(MAP_ROWS, r0 + sh // TILE + 2)
        
        for row in range(r0, r1):
            for col in range(c0, c1):
                sx = col*TILE - cx
                sy = row*TILE - cy
                v = self.data[row][col]
                
                if v == 1:
                    surface.blit(self.wall_surf, (sx, sy))
                elif v == 3:
                    surface.blit(self.hide_surf, (sx, sy))
                elif v == 2:
                    surface.blit(self.floor_surf, (sx, sy))
                    surface.blit(self.exit_surf, (sx, sy))
                    # Pulso da saída
                    pulse = 0.5 + 0.5 * math.sin(time * 3.0)
                    rs = int(TILE * 0.9 + pulse * 8)
                    glow = pygame.Surface((rs*2, rs*2), pygame.SRCALPHA)
                    pygame.draw.circle(glow, (*C_EXIT_GLOW, int(80*pulse)), (rs,rs), rs)
                    surface.blit(glow, (sx+TILE//2-rs, sy+TILE//2-rs), special_flags=pygame.BLEND_RGBA_ADD)
                else:
                    surface.blit(self.floor_surf, (sx, sy))