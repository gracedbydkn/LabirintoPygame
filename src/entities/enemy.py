# src/entities/enemy.py
import math
import random
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from src.core.config import TILE, MAZE_DATA, MAP_COLS, MAP_ROWS
from .actor import Actor

class EnemyAI(Actor):
    def __init__(self, x, y, sprite_manager):
        super().__init__(x, y, sprite_manager)
        self.state = 'WANDER'
        self.path = []
        self.finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
        
        # Pathfinding requer 1 para andável, <=0 para obstáculo.
        matrix = []
        for row in MAZE_DATA:
            # Transforma tudo que não é parede (1) em andável (1), e parede (1) em obstáculo (0)
            matrix.append([1 if cell in (0, 2, 3) else 0 for cell in row])
        self.grid = Grid(matrix=matrix)
        self.recalc_timer = 0

    def get_path(self, target_x, target_y):
        self.grid.cleanup()
        sx, sy = int(self.x // TILE), int(self.y // TILE)
        tx, ty = int(target_x // TILE), int(target_y // TILE)
        
        # Evita erro de índice fora da matriz
        sx = max(0, min(sx, MAP_COLS - 1))
        sy = max(0, min(sy, MAP_ROWS - 1))
        tx = max(0, min(tx, MAP_COLS - 1))
        ty = max(0, min(ty, MAP_ROWS - 1))
        
        start_node = self.grid.node(sx, sy)
        end_node = self.grid.node(tx, ty)
        
        if start_node.walkable and end_node.walkable:
            path, _ = self.finder.find_path(start_node, end_node, self.grid)
            return path
        return []

    def update(self, dt, player, walls):
        self.recalc_timer -= dt
        dist_to_player = math.hypot(player.x - self.x, player.y - self.y)
        
        # Transições de Estado
        if player.is_hidden:
            self.state = 'WANDER'
        elif dist_to_player < TILE * 7:
            self.state = 'CHASE'
        else:
            self.state = 'PATROL'

        if self.recalc_timer <= 0 or not self.path:
            if self.state == 'CHASE':
                self.path = self.get_path(player.x, player.y)
                self.recalc_timer = 0.3
                self.speed = 100
            elif self.state == 'PATROL':
                offset_x = player.x + random.randint(-TILE*4, TILE*4)
                offset_y = player.y + random.randint(-TILE*4, TILE*4)
                self.path = self.get_path(offset_x, offset_y)
                self.recalc_timer = 1.5
                self.speed = 80
            elif self.state == 'WANDER':
                rx, ry = random.randint(1, MAP_COLS-2), random.randint(1, MAP_ROWS-2)
                while MAZE_DATA[ry][rx] == 1:
                    rx, ry = random.randint(1, MAP_COLS-2), random.randint(1, MAP_ROWS-2)
                self.path = self.get_path(rx * TILE + TILE//2, ry * TILE + TILE//2)
                self.recalc_timer = 3.0
                self.speed = 50

        # Movimento ao longo do Path
        if self.path and len(self.path) > 1:
            next_node = self.path[1]
            target_x = next_node.x * TILE + TILE // 2
            target_y = next_node.y * TILE + TILE // 2
            
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.hypot(dx, dy)
            
            if dist < self.speed * dt:
                self.path.pop(0)
            else:
                self.vx = (dx / dist) * self.speed
                self.vy = (dy / dist) * self.speed
        else:
            self.vx = self.vy = 0

        self.x += self.vx * dt
        self.y += self.vy * dt
        self._resolve_collision(walls)

        if self.vx > 0.5: self.direction = 'right'
        elif self.vx < -0.5: self.direction = 'left'
        elif self.vy > 0.5: self.direction = 'down'
        elif self.vy < -0.5: self.direction = 'up'

        self.moving = abs(self.vx) > 0 or abs(self.vy) > 0
        if self.moving:
            self.frame_index = (self.frame_index + self.anim_speed * dt) % 9
        else:
            self.frame_index = 0