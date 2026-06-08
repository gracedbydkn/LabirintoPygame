# src/core/audio_manager.py
import pygame
import os

class AudioManager:
    def __init__(self, sfx_volume=0.8, ambient_volume=0.4):
        # Inicializa o mixer do pygame
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        self.sfx_volume = sfx_volume
        self.ambient_volume = ambient_volume

        # Dicionário de efeitos sonoros carregados: {"nome": Sound}
        self._sfx = {}

        # Canal dedicado para o som ambiente (loop contínuo)
        self._ambient_channel = pygame.mixer.Channel(0)
        self._ambient_channel.set_volume(self.ambient_volume)

    # ------------------------------------------------------------------ #
    #  Carregamento                                                        #
    # ------------------------------------------------------------------ #

    def load_sfx(self, name, filepath):
        """Carrega um efeito sonoro e armazena pelo nome."""
        if not os.path.exists(filepath):
            return
        sound = pygame.mixer.Sound(filepath)
        sound.set_volume(self.sfx_volume)
        self._sfx[name] = sound

    def load_ambient(self, filepath):
        """Carrega o som ambiente diretamente no mixer (stream)."""
        if not os.path.exists(filepath):
            return
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.set_volume(self.ambient_volume)

    # ------------------------------------------------------------------ #
    #  Reprodução                                                          #
    # ------------------------------------------------------------------ #

    def play_sfx(self, name):
        """Toca um efeito sonoro pelo nome. Ignora silenciosamente se não existir."""
        sound = self._sfx.get(name)
        if sound:
            sound.play()


    def play_ambient(self, loops=-1):
        """Inicia o som ambiente em loop. loops=-1 = infinito."""
        if pygame.mixer.music.get_busy():
            return
        pygame.mixer.music.play(loops)

    def stop_ambient(self):
        pygame.mixer.music.stop()

    # ------------------------------------------------------------------ #
    #  Volume                                                              #
    # ------------------------------------------------------------------ #

    def set_sfx_volume(self, volume):
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self._sfx.values():
            sound.set_volume(self.sfx_volume)

    def set_ambient_volume(self, volume):
        self.ambient_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.ambient_volume)