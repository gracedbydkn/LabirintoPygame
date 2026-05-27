# src/world/objects/vaso.py

from src.world.entities.world_object import WorldObject
from src.world.entities.interactable import Interactable

class Vaso(WorldObject):
    def __init__(self, x, y, frames, frames_highlight, frames_quebrado, loot_type=None):
        super().__init__(x, y, frames)
        self.frames_highlight = frames_highlight
        self.frames_quebrado = frames_quebrado
        self.loot_type = loot_type
        self.broken = False
        self.interactable = Interactable(
            on_interact=self._quebrar,
            prompt="Quebrar"
        )
    
    def draw(self, surface, camera):
        if self.broken:
            frames_ativos = self.frames_quebrado
        elif self.highlighted:
            frames_ativos = self.frames_highlight
        else:
            frames_ativos = self.frames

        frame = frames_ativos[int(self.frame_index) % len(frames_ativos)]
        sx = int(self.x - camera.x)
        sy = int(self.y - camera.y)
        fw, fh = frame.get_width(), frame.get_height()
        surface.blit(frame, (sx - fw // 2, sy - fh))

    def _quebrar(self, jogador):
        if self.loot_type:
            jogador.items_para_spawnar.append({
                "type": self.loot_type,
                "x": self.x,
                "y": self.y
            })
        
        self.broken = True
        self.interactable.enabled = False