#src/world/objects/barreira.py
from src.world.entities.world_object import WorldObject

class Barreira(WorldObject):
    def __init__(self, x, y, frames, runa_necessaria):
        super().__init__(x, y, frames)
        self.runa_necessaria = runa_necessaria

    def update(self, dt, jogador):
        dist = ((self.x - jogador.x)**2 + (self.y - jogador.y)**2) ** 0.5

        if dist <= jogador.interaction_range:
            if jogador.inventory.tem(self.runa_necessaria):
                jogador.inventory.remover(self.runa_necessaria)
                self.dead = True