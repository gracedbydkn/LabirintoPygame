# src/entities/actor.py
import pygame
from src.core.config import INIT_SCREEN_W

class Actor:
    def __init__(self, x, y, sprite_manager):
        # Posição inicial como float para permitir movimento com precisão sub-pixel
        self.x, self.y = float(x), float(y)

        # Velocidade inicial zerada nos dois eixos
        self.vx = self.vy = 0.0

        # Gerenciador de sprites com as animações do ator
        self.sprites = sprite_manager

        # Direção atual — controla qual animação exibir
        self.direction = 'down'

        # Índice do frame atual da animação (float para suportar velocidade fracionada)
        self.frame_index = 0

        # Velocidade de avanço dos frames de animação (frames por segundo lógico)
        self.anim_speed = 10

        # Indica se o ator está em movimento (usado para alternar idle/walk)
        self.moving = False

        # Raio do hitbox circular usado na detecção de colisão com paredes
        self.radius = 24

    def _resolve_collision(self, walls):
        """Resolve colisões entre o ator e uma lista de retângulos de parede.
        Usa sobreposição mínima (AABB) para empurrar o ator para fora da parede."""

        # Cria o retângulo de colisão centrado na posição atual do ator
        pr = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)

        for wr in walls:
            if not pr.colliderect(wr):
                continue  # Sem colisão com essa parede, pula

            # Calcula a sobreposição nos 4 lados
            ol = pr.right  - wr.left   # Sobreposição pela esquerda da parede
            or_= wr.right  - pr.left   # Sobreposição pela direita da parede
            ot = pr.bottom - wr.top    # Sobreposição pelo topo da parede
            ob = wr.bottom - pr.top    # Sobreposição pela base da parede

            # Resolve pelo eixo com menor sobreposição (empurrão mínimo)
            if min(ol, or_) < min(ot, ob):
                # Colisão horizontal: empurra no eixo X
                self.x -= ol if ol < or_ else -or_
            else:
                # Colisão vertical: empurra no eixo Y
                self.y -= ot if ot < ob else -ob

            # Atualiza o rect após o ajuste para checar próximas paredes corretamente
            pr = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)

    def draw(self, surface, camera, draw_scale=1.5):
        """Desenha o frame atual da animação na tela, centralizado na posição do ator."""

        # Converte posição do mundo para posição na tela usando o offset da câmera
        sx = int(self.x - camera.x)
        sy = int(self.y - camera.y)

        # Obtém o frame atual da animação conforme direção e índice
        frame = self.sprites.animations[self.direction][int(self.frame_index)]

        fw = frame.get_width()
        fh = frame.get_height()

        # Redimensiona o sprite se o fator de escala for diferente de 1
        if draw_scale != 1.0:
            frame = pygame.transform.scale(frame, (int(fw * draw_scale), int(fh * draw_scale)))
            fw = frame.get_width()
            fh = frame.get_height()

        # Desenha centralizado horizontalmente e com offset vertical de 90% da altura
        # (âncora na base do sprite, não no topo)
        surface.blit(frame, (sx - fw // 2, sy - int(fh * 0.9)))