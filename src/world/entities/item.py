# src/world/entities/item.py
import pygame

class Item:
    def __init__(self, x, y, item_type, frames, anim_speed=8):
        self.x = float(x)
        self.y = float(y)

        self.item_type = item_type

        # Aceita tanto um único Surface quanto uma lista de frames
        if isinstance(frames, list):
            self.frames = frames
        else:
            self.frames = [frames]

        self.anim_speed = anim_speed
        self.frame_index = 0.0

        self.rect = pygame.Rect(self.x - 16, self.y - 16, 32, 32)
        self.dead = False

    def update(self, dt):
        """Avança a animação do item."""
        if len(self.frames) > 1:
            self.frame_index = (self.frame_index + self.anim_speed * dt) % len(self.frames)

    def collect(self, jogador):
        """Coleta o item e o adiciona ao inventário do jogador."""
        jogador.inventory.adicionar(self)
        self.dead = True

    def draw(self, surface, camera):
        frame = self.frames[int(self.frame_index) % len(self.frames)]
        sx = int(self.x - camera.x)
        sy = int(self.y - camera.y)
        fw = frame.get_width()
        fh = frame.get_height()
        surface.blit(frame, (sx - fw // 2, sy - fh // 2))