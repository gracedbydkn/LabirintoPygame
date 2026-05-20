# src/entities/player.py
from .actor import Actor

class Player(Actor):
    def __init__(self, x, y, sprite_manager):
        super().__init__(x, y, sprite_manager)

        # Velocidade de movimento em pixels por segundo
        self.speed = 240

        # Flag que indica se o jogador está em um esconderijo (afeta detecção pelo inimigo)
        self.is_hidden = False

    def update(self, dt, walls):
        """Atualiza posição, colisão, direção e animação do jogador a cada frame."""

        # Aplica a velocidade ao longo do tempo (vx/vy são definidos pelo input externo)
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Corrige a posição caso haja sobreposição com alguma parede
        self._resolve_collision(walls)

        # Atualiza a direção visual com base na velocidade — prioridade: horizontal > vertical
        if self.vx > 0:
            self.direction = 'right'
        elif self.vx < 0:
            self.direction = 'left'
        elif self.vy > 0:
            self.direction = 'down'
        elif self.vy < -0.5:        # Limiar pequeno para evitar flip acidental na vertical
            self.direction = 'up'

        # Determina se está em movimento para controlar qual animação exibir
        self.moving = self.vx != 0 or self.vy != 0

        if self.moving:
            # Avança o frame da animação de caminhada proporcionalmente ao tempo
            self.frame_index = (self.frame_index + self.anim_speed * dt) % 9
        else:
            # Sem movimento: reseta para o frame 0 (pose idle)
            self.frame_index = 0