# src/entities/player.py

import pygame
from .actor import Actor
from .inventory import Inventory

class Player(Actor):
    def __init__(self, x, y, sprite_manager, joystick=None):
        super().__init__(x, y, sprite_manager)
        self.joystick = joystick

        # Velocidade de movimento em pixels por segundo
        self.base_speed = 220
        self.run_speed = 300
        self.speed = self.base_speed

        # --- Sistema de Stamina ---
        self.max_stamina = 100.0
        self.stamina = self.max_stamina
        self.stamina_drain = 35.0  # Zera em ~2.8 segundos de corrida contínua
        self.stamina_regen = 15.0  # Recupera tudo em ~6.6 segundos andando/parado
        self.exhausted = False     # Fica True se zerar a stamina
        self.is_running = False

        # Flag que indica se o jogador está em um esconderijo (afeta detecção pelo inimigo)
        self.is_hidden = False
        self.inventory = Inventory()
        self.interaction_range = 70
        self.items_para_spawnar = []
        self.venceu = False

    def _get_objeto_a_frente(self, world_objects, items):
        offsets = {
            'right': (self.interaction_range, 0),
            'left': (-self.interaction_range, 0),
            'down': (0, self.interaction_range),
            'up': (0, -self.interaction_range)
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

        # Para WorldObjects: exige estar olhando na direção (ex: quebrar vaso)
        alvo_objeto = self._get_objeto_a_frente(world_objects, [])
        if alvo_objeto and isinstance(alvo_objeto, WorldObject) and alvo_objeto.interactable:
            alvo_objeto.interactable.interact(self)
            return

        # Para Items: basta estar próximo (ex: pegar chave)
        alvo_item = self._get_objeto_proximo([], items)
        if alvo_item and isinstance(alvo_item, Item):
            alvo_item.collect(self)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        vx, vy = 0.0, 0.0
        
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  vx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: vx += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:    vy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  vy += 1

        trying_to_run = keys[pygame.K_LSHIFT]

        # --- Gamepad ---
        DEAD_ZONE = 0.15  # ignora ruído do analógico

        if pygame.joystick.get_count() > 0:
            joy = pygame.joystick.Joystick(0)

            # Analógico esquerdo (eixos 0 e 1)
            axis_x = joy.get_axis(0)
            axis_y = joy.get_axis(1)

            if abs(axis_x) > DEAD_ZONE: vx += axis_x
            if abs(axis_y) > DEAD_ZONE: vy += axis_y

            # D-pad (hat 0) — fallback caso o analógico não seja usado
            
            hat = joy.get_hat(0)
            vx += hat[0]   # -1 (esq), 0, +1 (dir)
            vy -= hat[1]   # hat Y é invertido no pygame

            if joy.get_button(2) or joy.get_button(5):
                trying_to_run = True

        direcao = pygame.Vector2(vx, vy)
        moving = direcao.length() > 0
        if moving:
            direcao.normalize_ip()

        if trying_to_run and moving and not self.exhausted:
            self.is_running = True
            self.speed = self.run_speed
        else:
            self.is_running = False
            self.speed = self.base_speed
        
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
        if self.vx > 0: self.direction = 'right'
        elif self.vx < 0: self.direction = 'left'
        elif self.vy > 0: self.direction = 'down'
        elif self.vy < -0.5: # Limiar pequeno para evitar flip acidental na vertical
            self.direction = 'up'

        # Determina se está em movimento para controlar qual animação exibir
        self.moving = self.vx != 0 or self.vy != 0

        # --- Gerenciamento da Stamina ---
        if self.is_running:
            self.stamina -= self.stamina_drain * dt
            if self.stamina <= 0:
                self.stamina = 0
                self.exhausted = True     # Punição: o jogador perdeu o fôlego
                self.is_running = False
                self.speed = self.base_speed
        else:
            self.stamina += self.stamina_regen * dt
            if self.stamina >= self.max_stamina:
                self.stamina = self.max_stamina
            
            # Condição para sair da exaustão: recuperar pelo menos 30% da barra
            if self.exhausted and self.stamina > self.max_stamina * 0.3:
                self.exhausted = False
                
        if self.is_running and self.moving:
            self.current_animation = f'run_{self.direction}' # 8 frames de corrida
            self.frame_index = (self.frame_index + self.anim_speed_run * dt) % 8
        elif self.moving:
            self.current_animation = self.direction          # 9 frames de caminhada
            self.frame_index = (self.frame_index + self.anim_speed * dt) % 9
        else:
            self.current_animation = f'idle_{self.direction}' # 2 frames de idle
            self.frame_index = (self.frame_index + self.anim_speed_idle * dt) % 2