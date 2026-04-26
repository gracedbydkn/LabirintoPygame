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
        self.state = 'WANDER'
        self.path = []
        self.finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
        self.recalc_timer = 0
        self.radius = 20
        self.last_known_pos = None

    def has_line_of_sight(self, target_x, target_y, maze):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        if dist == 0: return True
        
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
                    return False
        return True

    def is_facing_player(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        
        dirs = {'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1, 0)}
        fx, fy = dirs[self.direction]
        
        dist = math.hypot(dx, dy)
        if dist == 0: return True
        
        dot_product = (dx/dist)*fx + (dy/dist)*fy
        return dot_product > 0.5 

    def get_path(self, target_x, target_y, maze):
        pf_matrix = []
        for row in maze.matrix:
            pf_matrix.append([1 if cell != 1 else 0 for cell in row])
            
        grid = Grid(matrix=pf_matrix)
        sx, sy = int(self.x // maze.tile_size), int(self.y // maze.tile_size)
        tx, ty = int(target_x // maze.tile_size), int(target_y // maze.tile_size)
        
        sx = max(0, min(sx, maze.cols - 1))
        sy = max(0, min(sy, maze.rows - 1))
        tx = max(0, min(tx, maze.cols - 1))
        ty = max(0, min(ty, maze.rows - 1))
        
        start_node = grid.node(sx, sy)
        end_node = grid.node(tx, ty)
        
        if start_node.walkable and end_node.walkable:
            path, _ = self.finder.find_path(start_node, end_node, grid)
            return path
        return []

    def update(self, dt, player, maze):
        self.recalc_timer -= dt
        dist_to_player = math.hypot(player.x - self.x, player.y - self.y)
        
        # 1. Sensores
        can_see_player = False
        if not player.is_hidden:
            if dist_to_player < maze.tile_size * 2:
                can_see_player = True
            elif dist_to_player < (FOV_RADIUS + FOV_SOFT_EDGE):
                if self.is_facing_player(player) and self.has_line_of_sight(player.x, player.y, maze):
                    can_see_player = True

        # 2. Transições de Estado
        if player.is_hidden:
            self.state = 'WANDER'
        elif can_see_player:
            self.state = 'CHASE'
            self.last_known_pos = (player.x, player.y)
        elif self.state == 'CHASE' and not can_see_player:
            self.state = 'INVESTIGATE'
            self.recalc_timer = 0

        if self.state == 'INVESTIGATE' and self.last_known_pos:
            dist_to_last = math.hypot(self.last_known_pos[0] - self.x, self.last_known_pos[1] - self.y)
            if dist_to_last < 10:
                self.state = 'PATROL'
                self.last_known_pos = None
                self.recalc_timer = 0

        # 3. Cálculo de Rota
        if self.recalc_timer <= 0 or not self.path:
            if self.state == 'CHASE':
                self.path = self.get_path(player.x, player.y, maze)
                self.recalc_timer = 0.3
                self.speed = 260
            elif self.state == 'INVESTIGATE':
                if self.last_known_pos:
                    self.path = self.get_path(self.last_known_pos[0], self.last_known_pos[1], maze)
                    self.recalc_timer = 1.0
                    self.speed = 200
            elif self.state == 'PATROL':
                offset_x = self.x + random.randint(-maze.tile_size*4, maze.tile_size*4)
                offset_y = self.y + random.randint(-maze.tile_size*4, maze.tile_size*4)
                self.path = self.get_path(offset_x, offset_y, maze)
                self.recalc_timer = 1.5
                self.speed = 160  
            elif self.state == 'WANDER':
                rx, ry = random.randint(1, maze.cols-2), random.randint(1, maze.rows-2)
                while maze.matrix[ry][rx] == 1:
                    rx, ry = random.randint(1, maze.cols-2), random.randint(1, maze.rows-2)
                self.path = self.get_path(rx * maze.tile_size + maze.tile_size//2, ry * maze.tile_size + maze.tile_size//2, maze)
                self.recalc_timer = 3.0
                self.speed = 100

        # 4. Execução de Movimento
        if self.path:
            if len(self.path) > 1:
                next_node = self.path[1]
                target_x = next_node.x * maze.tile_size + maze.tile_size // 2
                target_y = next_node.y * maze.tile_size + maze.tile_size // 2
            else:
                if self.state == 'CHASE':
                    target_x = player.x
                    target_y = player.y
                elif self.state == 'INVESTIGATE' and self.last_known_pos:
                    target_x = self.last_known_pos[0]
                    target_y = self.last_known_pos[1]
                else:
                    target_x = self.x
                    target_y = self.y

            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.hypot(dx, dy)
            
            if dist < self.speed * dt:
                if len(self.path) > 1:
                    self.path.pop(0)
                else:
                    self.vx = self.vy = 0
            else:
                self.vx = (dx / dist) * self.speed
                self.vy = (dy / dist) * self.speed
        else:
            self.vx = self.vy = 0

        self.x += self.vx * dt
        self.y += self.vy * dt
        self._resolve_collision(maze.wall_rects)

        if self.vx > 0.5: self.direction = 'right'
        elif self.vx < -0.5: self.direction = 'left'
        elif self.vy > 0.5: self.direction = 'down'
        elif self.vy < -0.5: self.direction = 'up'

        self.moving = abs(self.vx) > 0 or abs(self.vy) > 0
        if self.moving:
            self.frame_index = (self.frame_index + self.anim_speed * dt) % 9
        else:
            self.frame_index = 0