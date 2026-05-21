# src/world/fog.py
import pygame
import math
from src.core.config import *

class FogOfWar:
    def __init__(self):
        # Cache para superfícies de gradiente já geradas — evita recriar a cada frame
        self._grad_cache = {}

    def _cast_ray(self, ox, oy, angle, max_dist, maze):
        """Lança um raio a partir da posição do jogador (ox, oy) em um dado ângulo.
        Retorna a distância percorrida até encontrar um obstáculo sólido."""
        dx = math.cos(angle)  # Componente X da direção do raio
        dy = math.sin(angle)  # Componente Y da direção do raio
        step = 4              # Tamanho do passo em pixels por iteração
        dist = 0.0
        hit_wall = False      # Indica se o raio já colidiu com uma parede

        while dist < max_dist:
            dist += step

            # Converte a posição do raio de pixels para coordenadas de grid (tile)
            tx = int((ox + dx * dist) // maze.tile_size)
            ty = int((oy + dy * dist) // maze.tile_size)

            # Se saiu dos limites do mapa, encerra o raio aqui
            if tx < 0 or ty < 0 or tx >= maze.cols or ty >= maze.rows:
                return dist

            if maze.matrix[ty][tx] == 1:
                # Entrou em uma parede — marca mas continua para revelar a face da parede
                hit_wall = True
            else:
                if hit_wall:
                    # Saiu da parede — revela a face e encerra o raio
                    return dist

        # Nenhum obstáculo encontrado: retorna a distância máxima
        return max_dist

    def _get_gradient(self, radius):
        """Cria (ou recupera do cache) uma superfície circular com transparência gradual.
        O centro é totalmente transparente e as bordas são opacas — simula a queda de luz."""
        if radius in self._grad_cache:
            return self._grad_cache[radius]

        size = int(radius * 2)
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))  # Começa totalmente transparente
        center = int(radius)

        # Desenha círculos concêntricos do maior para o menor, com alpha crescente nas bordas
        for r in range(int(radius), 0, -1):
            ratio = r / radius
            # Curva smoothstep: transição suave sem ser linear
            t = ratio * ratio * (3 - 2 * ratio)
            alpha = int(255 * (1 - t))  # Centro transparente → borda opaca
            pygame.draw.circle(surf, (255, 255, 255, alpha), (center, center), r)

        # Armazena no cache para reutilizar nos próximos frames
        self._grad_cache[radius] = surf
        return surf

    def draw(self, surface, player_x, player_y, camera, time, maze):
        """Renderiza a névoa de guerra sobre a superfície principal.
        O processo: cobre tudo de preto → abre um buraco onde o jogador enxerga."""
        w, h = surface.get_size()

        # --- Camada de névoa base ---
        fog = pygame.Surface((w, h), pygame.SRCALPHA)

        # Oscilação baseada em senos para simular tremulação de tocha/chama
        flicker = int(3 * math.sin(time * 7.3) + 2 * math.sin(time * 13.1))
        base_alpha = max(0, min(255, 240 + flicker))  # Limita entre 0 e 255
        fog.fill((0, 0, 0, base_alpha))  # Preenche a névoa com preto semi-opaco

        # --- Máscara de luz (área visível pelo jogador) ---
        light_mask = pygame.Surface((w, h), pygame.SRCALPHA)
        light_mask.fill((0, 0, 0, 0))  # Começa totalmente transparente

        # Posição do jogador na tela (descontando o offset da câmera)
        cx = player_x - camera.x
        cy = player_y - camera.y
        max_r = FOV_RADIUS + FOV_SOFT_EDGE

        # Lança todos os raios e coleta os pontos do polígono de visão
        pts = []
        for i in range(FOV_RAYS):
            angle = (i / FOV_RAYS) * math.tau  # math.tau = 2π (volta completa)
            dist = self._cast_ray(player_x, player_y, angle, max_r, maze)
            pts.append((int(cx + math.cos(angle) * dist), int(cy + math.sin(angle) * dist)))

        # Desenha o polígono de visão (área iluminada) na máscara
        if len(pts) >= 3:
            pygame.draw.polygon(light_mask, (255, 255, 255, 255), pts)

        # Aplica o gradiente sobre a máscara: suaviza as bordas da área visível
        grad = self._get_gradient(max_r)
        light_mask.blit(grad, grad.get_rect(center=(int(cx), int(cy))),
                        special_flags=pygame.BLEND_RGBA_MIN)  # Mantém o menor alpha pixel a pixel

        # Subtrai a máscara de luz da névoa — "abre o buraco" onde o jogador enxerga
        fog.blit(light_mask, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

        # Aplica a névoa final sobre a superfície do jogo
        surface.blit(fog, (0, 0))