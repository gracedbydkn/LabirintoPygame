#pip install pathfinding
#pip install pygame
#pip install pytmx

import pygame
import sys
from src.core.config import *
from src.utils.sprites import CharacterSprite, load_frames, load_spritesheet_row
from src.world.maze import Maze
from src.world.fog import FogOfWar
from src.world.entities.player import Player
from src.world.entities.enemy import EnemyAI
from src.world.env_object import EnvObject
from src.world.entities.world_object import WorldObject
from src.world.entities.item import Item
from src.world.objects.vaso import Vaso
from src.world.objects.barreira import Barreira
from src.world.objects.porta_saida import PortaSaida
from src.world.objects.esconderijo import Esconderijo


class Game:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"Controle conectado: {self.joystick.get_name()}")
        else:
            print("Nenhum controle encontrado")

        
        self.screen = pygame.display.set_mode((INIT_SCREEN_W, INIT_SCREEN_H), pygame.RESIZABLE)
        pygame.display.set_caption("Masmorra Dark Fantasy")
        self.clock = pygame.time.Clock()
        self.font_lg = pygame.font.SysFont("monospace", 40, bold=True)
        self.font_sm = pygame.font.SysFont("monospace", 20)
        
        try:
            self.sprite_player = CharacterSprite("assets/characters/player-spritesheet.png")
            self.sprite_zumbi = CharacterSprite("assets/characters/zumbi-spritesheet.png")
        except FileNotFoundError:
            print("Erro: Imagem não encontrada.")
            sys.exit(1)
            
        self.maze = Maze("assets/maps/catacombs/map.tmx", scale_factor=4)
        # Carrega frames de cada tipo de objeto animado do ambiente
        ts = self.maze.tile_size
        vaso_size = (int(ts*1.7), int(ts*1.7))
        vaso_frames = load_frames("assets/itens/vaso-frame-{}.png", 4, vaso_size)
        chave_size = (int(ts * 0.8), int(ts * 0.8))
        chave_frames = load_spritesheet_row("assets/itens/key_32x32_24f.png", 24, 32, 32, chave_size)
        runa_frames = load_frames("assets/itens/runa_azul{}.png", 2, (ts*4,ts*4))
        barreira_frames = load_frames("assets/itens/barreira-{}.png", 3, (ts*4.5, ts*4.5) )
        barril_frames = load_frames("assets/itens/barril-{}.png", 4, (ts*1.7, ts*1.7))

        self.env_frames = {
            "vaso": [vaso_frames[0]],
            "vaso_highlight": [vaso_frames[1]],
            "vaso_quebrado": [vaso_frames[3]],
            "torch": load_frames("assets/catacombs rogue fantasy/RF_Catacombs_v1.0/torch_{}.png", 4, (ts, ts)),
            "chave": chave_frames,
            "barreira": barreira_frames,
            "runa_azul": [runa_frames],
            "porta_saida": load_frames("assets/itens/porta_saida.png", 1, (ts*4, ts*4)),
            "barril": [barril_frames[0]],
            "barril_aberto": [barril_frames[1]],
            "barril_player": [barril_frames[2]],
            "barril_highlight": [barril_frames[3]]
        }
        self.fog = FogOfWar()
        self.camera = pygame.Vector2(0, 0)
        self.key_hints = self._carregar_teclas()
        self.reset()


    def reset(self):
        self.game_over = False
        self.won = False
        self.time = 0.0
        try:
            spawn_point = self.maze.tmx_data.get_object_by_name("start")
            spawn_x = spawn_point.x * self.maze.scale
            spawn_y = spawn_point.y * self.maze.scale
        except Exception:
            spawn_x = 8.5 * self.maze.tile_size
            spawn_y = 8.5 * self.maze.tile_size
            
        self.player = Player(spawn_x, spawn_y, self.sprite_player, joystick=self.joystick)
        enemy_x = 15.5 * self.maze.tile_size
        enemy_y = 10.5 * self.maze.tile_size
        self.enemy = EnemyAI(enemy_x, enemy_y, self.sprite_zumbi)
        
        sw, sh = self.screen.get_size()
        self.camera.x = self.player.x - sw / 2
        self.camera.y = self.player.y - sh / 2

        # Instancia objetos de ambiente a partir dos dados do Object Layer
        self.world_objects = []
        self.items = []
        self.items_para_spawnar = []
        self.env_objects = []

        for data in self.maze.env_object_data:
            print(f"objeto: name={data['name']}, type={data['type']}")
            if data["type"] == "vaso":
                frames   = self.env_frames.get("vaso")
                frames_h = self.env_frames.get("vaso_highlight")
                frames_q = self.env_frames.get("vaso_quebrado")
                if frames and frames_h and frames_q:
                    self.world_objects.append(Vaso(data["x"], data["y"], frames, frames_h, frames_q, loot_type=data["chave"]))
            elif data["type"] == "torch":
                frames = self.env_frames.get(data["type"])
                if frames:
                    self.env_objects.append(EnvObject(data["x"], data["y"], frames))
            elif data["type"] == "barreira":
                frames = self.env_frames.get("barreira")
                if frames:
                    self.world_objects.append(
                        Barreira(data["x"], data["y"], frames, runa_necessaria="runa_azul", anim_speed=8)
                    )
            elif data["type"] == "runa":
                frames = self.env_frames.get(data["name"])
                if frames:
                    self.items.append(
                        Item(data["x"], data["y"], data["name"], frames[0],)
                    )
            elif data["type"] == "porta_saida":
                frames = self.env_frames.get("porta_saida")
                if frames:
                    self.world_objects.append(
                        PortaSaida(data["x"], data["y"], frames, chave_necessaria="chave")
                    )
            elif data["type"] == "esconderijo":
                frames = self.env_frames.get("barril")
                frames_a = self.env_frames.get("barril_aberto")
                frames_p = self.env_frames.get("barril_player")
                frames_h = self.env_frames.get("barril_highlight")
                if frames and frames_a and frames_p and frames_h:
                    self.world_objects.append(
                        Esconderijo(data["x"], data["y"], frames, frames_a, frames_p, frames_h)
                    )
    

    def _carregar_tecla(self, nome, tamanho=(40, 40)):
        try:
            raw = pygame.image.load(f"assets/keyboard-keys/{nome}.png").convert_alpha()
            rw, rh = raw.get_size()
            fw = rw // 3
            return [
                pygame.transform.scale(raw.subsurface((i * fw, 0, fw, rh)), tamanho)
                for i in range(3)
            ]
        except (FileNotFoundError, pygame.error):
            return None

    def _carregar_teclas(self):
        nomes = ["E", "W", "A", "S", "D", "ARROWUP", "ARROWLEFT", "ARROWDOWN", "ARROWRIGHT"]
        return {n: self._carregar_tecla(n) for n in nomes}

    def draw_key_hints(self):
        # frame atual: normal (0) → pressionada (1) → subindo (2)
        ciclo = self.time % 0.86
        f = 0 if ciclo < 0.50 else (1 if ciclo < 0.68 else 2)

        # Tecla E acima do objeto interagível mais próximo
        alvo = self.player._get_objeto_proximo(self.world_objects, self.items)
        pode_interagir = (
            alvo and (
                (isinstance(alvo, Item) and not alvo.dead)
                or (hasattr(alvo, 'interactable') and alvo.interactable and alvo.interactable.enabled)
            )
        )
        if not pode_interagir:
            alvo = self.player._get_objeto_proximo([], self.items)
            pode_interagir = bool(alvo)
        frames = pode_interagir and self.key_hints.get("E")
        if frames:
            sx = int(alvo.x - self.camera.x)
            sy = int(alvo.y - self.camera.y) - 100
            frame = frames[f]
            self.screen.blit(frame, (sx - frame.get_width() // 2, sy - frame.get_height() // 2))

        # WASD / Setas após 5s parado — alterna a cada 3.5s
        if self.player.idle_time >= 5.0:
            sw, sh = self.screen.get_size()
            setas = int(self.player.idle_time / 3.5) % 2 == 1
            step = 44
            cx, cy = sw // 2, sh - 72
            teclas = (
                [("ARROWUP", cx, cy - step), ("ARROWLEFT", cx - step, cy),
                ("ARROWDOWN", cx, cy), ("ARROWRIGHT", cx + step, cy)]
                if setas else
                [("W", cx, cy - step), ("A", cx - step, cy),
                ("S", cx, cy), ("D", cx + step, cy)]
            )
            for nome, x, y in teclas:
                frames = self.key_hints.get(nome)
                if frames:
                    frame = frames[f]
                    self.screen.blit(frame, (x - frame.get_width() // 2, y - frame.get_height() // 2))
            

    def check_conditions(self):
        px_grid = int(self.player.x // self.maze.tile_size)
        py_grid = int(self.player.y // self.maze.tile_size)
        tile_value = self.maze.get_tile_value(px_grid, py_grid)
        
        # Se for 3, é esconderijo
        self.player.is_hidden = (tile_value == 3)

        # Condição de Derrota
        dist_to_enemy = ((self.player.x - self.enemy.x)**2 + (self.player.y - self.enemy.y)**2)**0.5
        if dist_to_enemy < 20:
            self.game_over = True

        # Condição de Vitória (Se o player passar pela porta final, ele ganha)
        if self.player.venceu:
            self.won = True

    def draw_ui_overlay(self, title, color, bg_color):
        sw, sh = self.screen.get_size()
        ov = pygame.Surface((sw, sh), pygame.SRCALPHA)
        ov.fill(bg_color)
        self.screen.blit(ov, (0,0))
        
        txt_title = self.font_lg.render(title, True, color)
        txt_sub = self.font_sm.render("R = Tentar Novamente  •  ESC = Sair", True, C_HUD_TEXT)
        
        self.screen.blit(txt_title, txt_title.get_rect(center=(sw//2, sh//2 - 20)))
        self.screen.blit(txt_sub, txt_sub.get_rect(center=(sw//2, sh//2 + 30)))

    def draw_hud(self):
        # Configurações da barra de stamina
        bar_width = 200
        bar_height = 15
        x_pos = 20
        y_pos = 20
        
        # Cores (muda para vermelho se estiver exausto)
        bg_color = (50, 50, 50, 180)
        stamina_color = (150, 50, 50) if self.player.exhausted else (50, 150, 50)
        
        # Calcula a porcentagem de stamina atual
        fill_width = int((self.player.stamina / self.player.max_stamina) * bar_width)
        
        # Fundo da barra
        pygame.draw.rect(self.screen, bg_color, (x_pos, y_pos, bar_width, bar_height))
        # Preenchimento da barra
        pygame.draw.rect(self.screen, stamina_color, (x_pos, y_pos, fill_width, bar_height))
        # Borda
        pygame.draw.rect(self.screen, (200, 200, 200), (x_pos, y_pos, bar_width, bar_height), 2)

    def run(self):
        while True:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            self.time += dt
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()
                    if event.key == pygame.K_r and (self.game_over or self.won):
                        self.reset()
                    if event.key == pygame.K_e:
                        self.player.interagir(self.world_objects, self.items)
                        
                # Gamepad — botões
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:  # A (Xbox) / Cruz (PS)
                        self.player.interagir(self.world_objects, self.items)

            self.player.handle_input()
            
            self.maze.object_rects =[obj.rect for obj in self.world_objects if obj.solid]
            if not self.game_over and not self.won:
                self.player.update(dt, self.maze.wall_rects+self.maze.object_rects)
                self.enemy.update(dt, self.player, self.maze)

                for obj in self.env_objects:
                    obj.update(dt)
                for obj in self.world_objects:
                    if hasattr(obj, 'update') and 'jogador' in obj.update.__code__.co_varnames:
                        obj.update(dt, self.player)
                    else:
                        obj.highlighted = False
                        obj.update(dt)
                   
                for item in self.items:
                    item.update(dt)
                alvo = self.player._get_objeto_proximo(self.world_objects, self.items)
                if alvo and hasattr(alvo, 'highlighted'):
                    alvo.highlighted = True

                self.world_objects = [o for o in self.world_objects if not o.dead]
                self.items = [i for i in self.items if not i.dead]
                self.items_para_spawnar.extend(self.player.items_para_spawnar)
                self.player.items_para_spawnar.clear()

                for spawn in self.items_para_spawnar:
                    frames = self.env_frames.get(spawn["type"])
                    if frames:
                        self.items.append(Item(spawn["x"], spawn["y"], spawn["type"], frames))
                self.items_para_spawnar.clear()

                self.check_conditions()

            sw, sh = self.screen.get_size()
            target_x = self.player.x - sw / 2
            target_y = self.player.y - sh / 2
            self.camera.x += (target_x - self.camera.x) * 0.08
            self.camera.y += (target_y - self.camera.y) * 0.08

            self.screen.fill(C_BG)
            self.maze.draw(self.screen, self.camera, self.time)
            
            # Entidades e objetos de ambiente ordenados por Y para depth sorting correto
            drawables = ([] if self.player.is_hidden else [self.player])
            drawables += [self.enemy] + self.env_objects + self.world_objects + self.items
            drawables.sort(key=lambda e: e.y)
            for e in drawables:
                e.draw(self.screen, self.camera)
                self.maze.draw_top(self.screen, self.camera)
            if not self.won:
                tochas = [(obj.x, obj.y) for obj in self.env_objects]
                self.fog.draw(self.screen, self.player.x, self.player.y, self.camera, self.time, self.maze, tochas)
            if not self.game_over and not self.won:
                self.draw_hud()

            self.draw_key_hints()
                
            if self.game_over:
                self.draw_ui_overlay("VOCÊ FOI PEGO!", (255, 50, 50), (60, 0, 0, 180))
            elif self.won:
                self.draw_ui_overlay("VOCÊ ESCAPOU!", C_EXIT, (10, 30, 10, 180))

            pygame.display.flip()

if __name__ == "__main__":
    Game().run()