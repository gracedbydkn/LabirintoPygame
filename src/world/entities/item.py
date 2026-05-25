# src/world/entities/item.py
import pygame

class Item:
    def __init__(self, x, y, item_type, frame):
        self.x = float(x)
        self.y = float(y)

        self.item_type = item_type
        self.frame = frame
        self.rect = pygame.Rect(self.x - 16, self.y - 16, 32, 32)

        self.dead = False

    def collect(self, jogador):
        jogador.inventory.adicionar(self)
        self.dead = True
    
    def draw(self, surface, camera):
        sx = int(self.x - camera.x)
        sy = int(self.y - camera.y)
        fw = self.frame.get_width()
        fh = self.frame.get_height()
        surface.blit(self.frame, (sx - fw // 2, sy - fh // 2))