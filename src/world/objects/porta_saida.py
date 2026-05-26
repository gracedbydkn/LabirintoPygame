# src/world/objects/porta_saida.py
from src.world.entities.world_object import WorldObject
from src.world.entities.interactable import Interactable

class PortaSaida(WorldObject):
    def __init__(self, x, y, frames, chave_necessaria):
        super().__init__(x, y, frames)
        self.chave_necessaria = chave_necessaria

        self.interactable = Interactable(
            on_interact=self._abrir,
            prompt="Abrir"
        )

    def _abrir(self, jogador):
        if jogador.inventory.tem(self.chave_necessaria):
            jogador.inventory.remover(self.chave_necessaria)
            jogador.venceu = True
        # else: "voce precisa de uma chave" ou algo para a hud do jogo