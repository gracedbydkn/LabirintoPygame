# src/utils/sprites.py
import pygame

class CharacterSprite:
    def __init__(self, filepath):
        self.sheet = pygame.image.load(filepath).convert_alpha()
        self.frame_w = 64
        self.frame_h = 64
        self.animations = {
            'up': self._extract_row(8, 9),
            'left': self._extract_row(9, 9),
            'down': self._extract_row(10, 9),
            'right': self._extract_row(11, 9)
        }

    def _extract_row(self, row, num_frames):
        frames = []
        for col in range(num_frames):
            x = col * self.frame_w
            y = row * self.frame_h
            surf = pygame.Surface((self.frame_w, self.frame_h), pygame.SRCALPHA)
            surf.blit(self.sheet, (0, 0), (x, y, self.frame_w, self.frame_h))
            frames.append(surf)
        return frames