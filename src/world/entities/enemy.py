# src/entities/enemy.py
import math
import random
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from src.core.config import FOV_RADIUS, FOV_SOFT_EDGE
from .actor import Actor

class EnemyAI(Actor):
    def __init__(self, x, y, sprite_manager):
        super().__init__(x, y, sprite_manager)

        # Estado inicial da máquina de estados do inimigo
        self.state = 'WANDER'

        # Caminho atual calculado pelo A* (lista de nós)
        self.path = []

        # Instância do algoritmo A* sem movimento diagonal
        self.finder = AStarFinder(diagonal_movement=DiagonalMovement.never)

        # Temporizador que controla quando recalcular o caminho
        self.recalc_timer = 0.0

        # Raio de colisão levemente menor que o do player
        self.radius = 20

        # Última posição conhecida do jogador (usada no estado INVESTIGATE)
        self.last_known_pos = None

        # Pontos de patrulha (não usados diretamente aqui, reservado para extensão)
        self.patrol_points = []
        self.patrol_index = 0

        # Tempo que o inimigo fica em alerta antes de partir para perseguição
        self.alert_timer = 0.0

    def has_line_of_sight(self, target_x, target_y, maze):
        """Verifica se há linha de visão direta entre o inimigo e o alvo,
        sem paredes bloqueando o caminho."""
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return True  # Mesmo ponto, visão garantida

        # Divide o segmento em passos de meio tile para não pular paredes finas
        step = maze.tile_size / 2
        steps = int(dist / step)
        dir_x = dx / dist
        dir_y = dy / dist

        for i in range(steps):
            cx = self.x + dir_x * (i * step)
            cy = self.y + dir_y * (i * step)
            tx = int(cx // maze.tile_size)
            ty = int(cy // maze.tile_size)
            if 0 <= tx < maze.cols and 0 <= ty < maze.rows:
                if maze.matrix[ty][tx] == 1:
                    return False  # Parede encontrada — visão bloqueada
        return True

    def is_facing_player(self, player):
        """Retorna True se o inimigo estiver olhando razoavelmente na direção do jogador.
        Usa produto escalar: dot > 0.5 equivale a um cone de ~60° de visão."""
        dx = player.x - self.x
        dy = player.y - self.y
        dirs = {'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1, 0)}
        fx, fy = dirs[self.direction]  # Vetor unitário da direção atual
        dist = math.hypot(dx, dy)
        if dist == 0:
            return True
        # Produto escalar entre a direção do inimigo e o vetor até o jogador
        dot = (dx / dist) * fx + (dy / dist) * fy
        return dot > 0.5

    def get_path(self, target_x, target_y, maze):
        """Calcula um caminho A* do inimigo até a posição alvo.
        Converte a matrix do labirinto para o formato do pathfinding (1=caminhável, 0=parede)."""
        pf_matrix = [[1 if cell != 1 else 0 for cell in row] for row in maze.matrix]
        grid = Grid(matrix=pf_matrix)

        # Converte posições em pixels para coordenadas de grid, com clamping nos limites
        sx = max(0, min(int(self.x // maze.tile_size), maze.cols - 1))
        sy = max(0, min(int(self.y // maze.tile_size), maze.rows - 1))
        tx = max(0, min(int(target_x // maze.tile_size), maze.cols - 1))
        ty = max(0, min(int(target_y // maze.tile_size), maze.rows - 1))

        start = grid.node(sx, sy)
        end   = grid.node(tx, ty)

        # Só calcula se origem e destino forem tiles caminháveis
        if start.walkable and end.walkable:
            path, _ = self.finder.find_path(start, end, grid)
            return path
        return []

    def _random_walkable_pos(self, maze):
        """Sorteia uma posição aleatória caminhável no mapa.
        Tenta até 50 vezes antes de desistir e retornar a posição atual."""
        for _ in range(50):
            rx = random.randint(1, maze.cols - 2)
            ry = random.randint(1, maze.rows - 2)
            if maze.matrix[ry][rx] != 1:
                # Retorna o centro do tile sorteado em pixels
                return rx * maze.tile_size + maze.tile_size // 2, ry * maze.tile_size + maze.tile_size // 2
        return self.x, self.y  # Fallback: fica no lugar

    def _move_along_path(self, dt, maze, override_target=None):
        """Avança o inimigo pelo caminho calculado, nó a nó.
        Retorna True quando o destino foi alcançado."""
        if not self.path:
            self.vx = self.vy = 0
            return True

        # Sempre mira no segundo nó do caminho (o próximo passo imediato)
        if len(self.path) > 1:
            node = self.path[1]
            target_x = node.x * maze.tile_size + maze.tile_size // 2
            target_y = node.y * maze.tile_size + maze.tile_size // 2
        else:
            # Último nó: usa override_target se disponível (ex: posição exata do jogador)
            if override_target:
                target_x, target_y = override_target
            else:
                self.vx = self.vy = 0
                return True

        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)

        # Se chegou perto o suficiente do nó atual, avança para o próximo
        if dist < self.speed * dt + 2:
            if len(self.path) > 1:
                self.path.pop(0)
                return False
            else:
                self.vx = self.vy = 0
                return True
        else:
            # Move na direção do próximo nó à velocidade configurada
            self.vx = (dx / dist) * self.speed
            self.vy = (dy / dist) * self.speed
            return False

    def update(self, dt, player, maze):
        """Loop principal da IA: atualiza sensores, máquina de estados, rota e movimento."""
        self.recalc_timer -= dt
        dist_to_player = math.hypot(player.x - self.x, player.y - self.y)

        # --- Sensores ---
        can_see_player = False
        if not player.is_hidden:
            # Detecção por proximidade extrema (independente de direção)
            too_close = dist_to_player < maze.tile_size * 1.5
            # Detecção por campo de visão: dentro do raio + olhando + sem obstáculo
            in_fov = (dist_to_player < (FOV_RADIUS + FOV_SOFT_EDGE)
                      and self.is_facing_player(player)
                      and self.has_line_of_sight(player.x, player.y, maze))
            can_see_player = too_close or in_fov

        # --- Máquina de Estados ---
        if player.is_hidden:
            # Jogador se escondeu: interrompe perseguição e vai investigar
            if self.state in ('CHASE', 'ALERT'):
                self.state = 'INVESTIGATE'
                self.recalc_timer = 0

        elif can_see_player:
            if self.state in ('WANDER', 'PATROL'):
                # Primeira vez avistando o jogador: pausa em ALERT antes de perseguir
                self.state = 'ALERT'
                self.last_known_pos = (player.x, player.y)
                self.alert_timer = random.uniform(0.6, 1.2)  # Reação entre 0.6s e 1.2s
                self.recalc_timer = 0

            elif self.state == 'ALERT':
                self.last_known_pos = (player.x, player.y)
                self.alert_timer -= dt
                if self.alert_timer <= 0:
                    # Tempo de alerta esgotado: parte para perseguição
                    self.state = 'CHASE'
                    self.recalc_timer = 0

            elif self.state in ('CHASE', 'INVESTIGATE'):
                # Já estava perseguindo: mantém CHASE e atualiza posição
                self.state = 'CHASE'
                self.last_known_pos = (player.x, player.y)

        else:
            # Perdeu o jogador de vista durante a perseguição
            if self.state == 'CHASE':
                self.state = 'INVESTIGATE'
                self.recalc_timer = 0

        # INVESTIGATE: verifica se chegou na última posição conhecida do jogador
        if self.state == 'INVESTIGATE' and self.last_known_pos:
            d = math.hypot(self.last_known_pos[0] - self.x, self.last_known_pos[1] - self.y)
            if d < maze.tile_size * 0.6:
                # Chegou no ponto — jogador não está aqui, entra em patrulha
                self.state = 'PATROL'
                self.last_known_pos = None
                self.recalc_timer = 0

        # --- Cálculo de Rota (recalcula quando o timer zera ou o caminho acaba) ---
        if self.recalc_timer <= 0 or not self.path:
            if self.state == 'CHASE':
                self.path = self.get_path(player.x, player.y, maze)
                self.recalc_timer = 0.25   # Recalcula frequentemente para seguir o jogador
                self.speed = 250           # Velocidade máxima

            elif self.state == 'ALERT':
                # Fica parado — só vira na direção do jogador (tratado na seção de movimento)
                self.speed = 0
                self.vx = self.vy = 0

            elif self.state == 'INVESTIGATE':
                if self.last_known_pos:
                    self.path = self.get_path(self.last_known_pos[0], self.last_known_pos[1], maze)
                    self.recalc_timer = 1.0
                    self.speed = 190

            elif self.state == 'PATROL':
                # Anda aleatoriamente em torno da área onde viu o jogador
                ox = self.x + random.randint(-maze.tile_size * 5, maze.tile_size * 5)
                oy = self.y + random.randint(-maze.tile_size * 5, maze.tile_size * 5)
                self.path = self.get_path(ox, oy, maze)
                self.recalc_timer = 2.5
                self.speed = 150

            elif self.state == 'WANDER':
                # Vagueia aleatoriamente pelo mapa em velocidade baixa
                wx, wy = self._random_walkable_pos(maze)
                self.path = self.get_path(wx, wy, maze)
                self.recalc_timer = 4.0
                self.speed = 90

        # --- Execução de Movimento ---
        if self.state == 'ALERT':
            # Em alerta: vira para o jogador mas não se move
            dx = player.x - self.x
            dy = player.y - self.y
            if abs(dx) > abs(dy):
                self.direction = 'right' if dx > 0 else 'left'
            else:
                self.direction = 'down' if dy > 0 else 'up'
            self.vx = self.vy = 0

        elif self.state == 'CHASE' and self.path:
            # Em perseguição: usa posição exata do jogador quando está no último nó
            override = (player.x, player.y) if len(self.path) <= 1 else None
            self._move_along_path(dt, maze, override)

        elif self.state == 'INVESTIGATE' and self.path:
            # Investigando: usa a última posição conhecida como alvo final
            override = self.last_known_pos if len(self.path) <= 1 else None
            self._move_along_path(dt, maze, override)

        else:
            self._move_along_path(dt, maze)

        # Aplica velocidade e resolve colisões com paredes
        self.x += self.vx * dt
        self.y += self.vy * dt
        self._resolve_collision(maze.wall_rects)

        # Atualiza a direção visual baseada no vetor de movimento (apenas se estiver andando)
        if abs(self.vx) > 0.5 or abs(self.vy) > 0.5:
            if abs(self.vx) >= abs(self.vy):
                self.direction = 'right' if self.vx > 0 else 'left'
            else:
                self.direction = 'down' if self.vy > 0 else 'up'

        # Avança o frame de animação se estiver em movimento, ou reseta para idle
        self.moving = abs(self.vx) > 1 or abs(self.vy) > 1
        if self.moving:
            self.frame_index = (self.frame_index + self.anim_speed * dt) % 9
        else:
            self.frame_index = 0  # Frame parado (idle)