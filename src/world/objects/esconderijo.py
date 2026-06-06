#src/world/objects/esconderijo.py
from src.world.entities.world_object import WorldObject
from src.world.entities.interactable import Interactable

class Esconderijo(WorldObject):
    def __init__(self, x, y, frames, frames_highlight):
        super().__init__(x, y, frames)

        self.interactable = Interactable(
            on_interact=self._alternar,
            prompt="Esconder-se"
        )
    
    def _alternar(self, jogador):
        # Alterna entre entrar e sair do esconderijo.
        if jogador.is_hidden:
            jogador.is_hidden = False
            jogador.esconderijo_atual = None
            self.interactable.prompt = "Esconder-se"
        else:
            jogador.is_hidden = True
            jogador.esconderijo_atual = self # Referência para saber onde está
            self.interactable.prompt = "Sair"