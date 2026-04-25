# src/entities/player.py
from .actor import Actor

class Player(Actor):
    def __init__(self, x, y, sprite_manager):
        super().__init__(x, y, sprite_manager)
        self.speed = 120
        self.is_hidden = False

    def update(self, dt, walls):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self._resolve_collision(walls)
        
        if self.vx > 0: self.direction = 'right'
        elif self.vx < 0: self.direction = 'left'
        elif self.vy > 0: self.direction = 'down'
        elif self.vy < 0: self.direction = 'up'

        self.moving = self.vx != 0 or self.vy != 0
        if self.moving:
            self.frame_index = (self.frame_index + self.anim_speed * dt) % 9
        else:
            self.frame_index = 0