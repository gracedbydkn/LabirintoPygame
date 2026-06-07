#src/world/objects/barreira.py
import pygame
from src.world.entities.world_object import WorldObject

class Barreira(WorldObject):
    def __init__(self, x, y, frames, runa_necessaria, anim_speed=8):
        super().__init__(x, y, frames, anim_speed=anim_speed)
        colisao_w = 350
        colisao_h = 100
        self.rect = pygame.Rect(
            self.x - colisao_w // 2,
            self.y - colisao_h,
            colisao_w,
            colisao_h
        )
        self.runa_necessaria = runa_necessaria

    def update(self, dt, jogador):
        super().update(dt)
        dist = ((self.x - jogador.x)**2 + (self.y - jogador.y)**2) ** 0.5

        if dist <= jogador.interaction_range:
            if jogador.inventory.tem(self.runa_necessaria):
                jogador.inventory.remover(self.runa_necessaria)
                self.dead = True