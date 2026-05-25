# src/world/entities/interactable.py

class Interactable:
    def __init__(self, on_interact, prompt="Interagir"):
        self.on_interact = on_interact
        self.prompt = prompt
        self.enabled = True
    
    def interact(self, jogador):
        if self.enabled:
            self.on_interact(jogador)