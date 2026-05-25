# src/entities/player.py

import pygame
from .actor import Actor
from .inventory import Inventory

class Player(Actor):
    def __init__(self, x, y, sprite_manager):
        super().__init__(x, y, sprite_manager)

        # Velocidade de movimento em pixels por segundo
        self.speed = 240
        # Flag que indica se o jogador está em um esconderijo (afeta detecção pelo inimigo)
        self.is_hidden = False
        self.inventory = Inventory()
        self.interaction_range = 70
        self.items_para_spawnar = []

    def _get_objeto_a_frente(self, world_objects, items):
        offsets = {
            'right': (self.interaction_range, 0),
            'left': (-self.interaction_range, 0),
            'down': (0, self.interaction_range),
            'up': (0, self.interaction_range)
        }
        ox, oy = offsets[self.direction]
        px = self.x + ox
        py = self.y + oy

        for obj in world_objects:
            if obj.rect.collidepoint(px, py):
                return obj

        for item in items:
            if item.rect.collidepoint(px, py):
                return item
        
        return None
    
    def _get_objeto_proximo(self, world_objects, items):
        for obj in world_objects:
            dist = ((self.x - obj.x)**2 + (self.y - obj.y)**2) ** 0.5
            if dist <= self.interaction_range:
                return obj
        for item in items:
            dist = ((self.x - item.x)**2 + (self.y - item.y)**2) ** 0.5
            if dist <= self.interaction_range:
                return item
        return None
    
    def interagir(self, world_objects, items):
        from .item import Item
        from .world_object import WorldObject

        alvo = self._get_objeto_a_frente(world_objects, items)
        if alvo is None:
            return
        
        if isinstance(alvo, Item):
            alvo.collect(self)

        elif isinstance(alvo, WorldObject) and alvo.interactable:
            alvo.interactable.interact(self)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        vx, vy = 0.0, 0.0
        
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  vx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: vx += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:    vy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  vy += 1

        direcao = pygame.Vector2(vx, vy)
        if direcao.length() > 0:
            direcao.normalize_ip()
        
        self.vx = direcao.x * self.speed
        self.vy = direcao.y * self.speed

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