# src/world/entities/world_object.py
import pygame
from .interactable import Interactable

class WorldObject:
    def __init__(self, x, y, frames, anim_speed=0):
        self.x = float(x)
        self.y = float(y)

        self.frames = frames
        self.anim_speed = anim_speed
        self.frame_index = 0.0
        

        self.radius = 24
        frame_w = frames[0].get_width()
        frame_h = frames[0].get_height()
        self.rect = pygame.Rect(
            self.x - frame_w // 2,
            self.y - frame_h,
            frame_w,
            frame_h,
        )

        self.interactable: Interactable | None = None
        self.highlighted = False
        self.solid = True
        self.dead = False
    
    def update(self, dt):
        if self.anim_speed > 0 and len(self.frames) > 1:
            self.frame_index = (self.frame_index + self.anim_speed * dt) % len(self.frames)
    
    def draw(self, surface, camera):
        frame = self.frames[int(self.frame_index)]
        sx = int(self.x - camera.x)
        sy = int(self.y - camera.y)
        fw = frame.get_width()
        fh = frame.get_height()
        surface.blit(frame, (sx - fw // 2, sy - fh))

    def kill(self):
        self.dead = True