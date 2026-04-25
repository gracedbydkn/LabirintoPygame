# src/entities/actor.py
import pygame

class Actor:
    def __init__(self, x, y, sprite_manager):
        self.x, self.y = float(x), float(y)
        self.vx = self.vy = 0.0
        self.sprites = sprite_manager
        self.direction = 'down'
        self.frame_index = 0
        self.anim_speed = 10
        self.moving = False
        self.radius = 12

    def _resolve_collision(self, walls):
        pr = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)
        for wr in walls:
            if not pr.colliderect(wr): continue
            ol = pr.right - wr.left
            or_ = wr.right - pr.left
            ot = pr.bottom - wr.top
            ob = wr.bottom - pr.top
            
            if min(ol, or_) < min(ot, ob):
                self.x -= ol if ol < or_ else -or_
            else:
                self.y -= ot if ot < ob else -ob
            pr = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)

    def draw(self, surface, camera):
        sx = int(self.x - camera.x)
        sy = int(self.y - camera.y)
        frame = self.sprites.animations[self.direction][int(self.frame_index)]
        surface.blit(frame, (sx - 32, sy - 48))