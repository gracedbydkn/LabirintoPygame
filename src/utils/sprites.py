# src/utils/sprites.py
import pygame

class CharacterSprite:
    def __init__(self, filepath, scale=1.0):
        raw_sheet = pygame.image.load(filepath).convert_alpha()
        w, h = raw_sheet.get_size()
        new_w = int(w * scale)
        new_h = int(h * scale)
        self.sheet = pygame.transform.scale(raw_sheet, (new_w, new_h))
        
        self.scale = scale
        self.frame_w = int(64 * scale)
        self.frame_h = int(64 * scale)
        
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