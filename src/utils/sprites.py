# src/utils/sprites.py
import pygame

class CharacterSprite:
    def __init__(self, filepath, scale=1.5):
        raw_sheet = pygame.image.load(filepath).convert_alpha()
        w, h = raw_sheet.get_size()
        new_w = int(w * scale)
        new_h = int(h * scale)
        self.sheet = pygame.transform.scale(raw_sheet, (new_w, new_h))
        
        self.scale = scale
        self.frame_w = int(64 * scale)
        self.frame_h = int(64 * scale)
        
        self.animations = {
            'idle_up': self._extract_row(22, 2),
            'idle_left': self._extract_row(23, 2),
            'idle_down': self._extract_row(24, 2),
            'idle_right': self._extract_row(25, 2),
            'up': self._extract_row(8, 9),
            'left': self._extract_row(9, 9),
            'down': self._extract_row(10, 9),
            'right': self._extract_row(11, 9)
        }

    def _extract_row(self, row, num_frames):
        frames = []
        for col in range(num_frames):
            x = col * self.frame_w
            y = row * self.frame_h
            surf = pygame.Surface((self.frame_w, self.frame_h), pygame.SRCALPHA)
            surf.blit(self.sheet, (0, 0), (x, y, self.frame_w, self.frame_h))
            frames.append(surf)
        return frames
    
def load_frames(pattern, count, size):
    # Carrega uma sequência de frames a partir de um padrão de nome
    # pattern: caminho com {} onde vai o índice  ex: "assets/itens/vaso-frame-{}.png"
    # count:   número de frames
    # size:    tupla (largura, altura) para escalar

    return [
        pygame.transform.scale(
            pygame.image.load(pattern.format(i)).convert_alpha(),
            size
        )
        for i in range(count)
    ]

def load_spritesheet_row(filepath, num_frames, frame_w, frame_h, scale_size=None):
    """Extrai frames de uma única linha horizontal de um spritesheet.
    
    filepath:   caminho para o PNG
    num_frames: número de frames na linha
    frame_w:    largura de cada frame no spritesheet original
    frame_h:    altura de cada frame no spritesheet original
    scale_size: tupla (w, h) para redimensionar cada frame — opcional
    """
    sheet = pygame.image.load(filepath).convert_alpha()
    frames = []
    for i in range(num_frames):
        surf = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
        surf.blit(sheet, (0, 0), (i * frame_w, 0, frame_w, frame_h))
        if scale_size:
            surf = pygame.transform.scale(surf, scale_size)
        frames.append(surf)
    return frames