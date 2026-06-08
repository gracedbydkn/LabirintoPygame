# src/world/objects/esconderijo.py
import pygame
from src.world.entities.world_object import WorldObject
from src.world.entities.interactable import Interactable

class Esconderijo(WorldObject):
    def __init__(self, x, y, frames, frames_highlight, frames_player, frames_aberto, on_hide=None):
        super().__init__(x, y, frames)
        colisao_w = 40
        colisao_h = 40
        self.rect = pygame.Rect(
            self.x - colisao_w // 2,
            self.y - colisao_h,
            colisao_w,
            colisao_h
        )

        self.frames_highlight = frames_highlight
        self.frames_player   = frames_player  # sprite com jogador dentro
        self.ocupado = False
        self.on_hide = on_hide
        self.interactable = Interactable(
            on_interact=self._alternar,
            prompt="Esconder"
        )

    def draw(self, surface, camera):
        if self.ocupado:
            frames_ativos = self.frames_player
        elif self.highlighted:
            frames_ativos = self.frames_highlight
        else:
            frames_ativos = self.frames

        frame = frames_ativos[int(self.frame_index) % len(frames_ativos)]
        sx = int(self.x - camera.x)
        sy = int(self.y - camera.y)
        fw, fh = frame.get_width(), frame.get_height()
        surface.blit(frame, (sx - fw // 2, sy - fh))

    def _alternar(self, jogador):
        if self.on_hide:
                self.on_hide()
        if jogador.is_hidden:
            jogador.is_hidden = False
            jogador.esconderijo_atual = None
            self.ocupado = False
            self.interactable.prompt = "Esconder"
        else:
            jogador.is_hidden = True
            jogador.esconderijo_atual = self
            self.ocupado = True
            self.interactable.prompt = "Sair"
            