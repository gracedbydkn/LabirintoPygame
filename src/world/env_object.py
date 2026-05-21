# src/world/env_object.py
import pygame

class EnvObject:
    """Objeto de ambiente com animação — tocha, vela, spike, etc.
    Segue o mesmo contrato de update/draw das entidades."""

    def __init__(self, x, y, frames, anim_speed=8):
        # Posição fixa no mundo em pixels (já com scale aplicado)
        self.x = float(x)
        self.y = float(y)

        # Lista de superfícies pygame representando cada frame da animação
        self.frames = frames

        # Velocidade de avanço dos frames (frames por segundo lógico)
        self.anim_speed = anim_speed

        # Índice do frame atual como float para suportar velocidade fracionada
        self.frame_index = 0.0

    def update(self, dt):
        """Avança o frame da animação proporcionalmente ao tempo."""
        self.frame_index = (self.frame_index + self.anim_speed * dt) % len(self.frames)

    def draw(self, surface, camera):
        """Desenha o frame atual centralizado horizontalmente, ancorado na base."""
        frame = self.frames[int(self.frame_index)]
        sx = int(self.x - camera.x)
        sy = int(self.y - camera.y)
        fw = frame.get_width()
        fh = frame.get_height()
        surface.blit(frame, (sx - fw // 2, sy - fh))