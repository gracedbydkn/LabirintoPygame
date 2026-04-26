#pip install pathfinding
#pip install pygame
#pip install pytmx

import pygame
import sys
from src.core.config import *
from src.utils.sprites import CharacterSprite
from src.world.maze import Maze
from src.world.fog import FogOfWar
from src.entities.player import Player
from src.entities.enemy import EnemyAI

class Game:
    def __init__(self):
        pygame.init()
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
            
        self.maze = Maze("assets/maps/mapteste/map.tmx", scale_factor=4)
        self.fog = FogOfWar()
        self.camera = pygame.Vector2(0, 0)
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
            
        self.player = Player(spawn_x, spawn_y, self.sprite_player)
        enemy_x = 15.5 * self.maze.tile_size
        enemy_y = 10.5 * self.maze.tile_size
        self.enemy = EnemyAI(enemy_x, enemy_y, self.sprite_zumbi)
        
        sw, sh = self.screen.get_size()
        self.camera.x = self.player.x - sw / 2
        self.camera.y = self.player.y - sh / 2

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.player.vx = self.player.vy = 0.0
        
        if not self.game_over and not self.won:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:  self.player.vx -= self.player.speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.player.vx += self.player.speed
            if keys[pygame.K_w] or keys[pygame.K_UP]:    self.player.vy -= self.player.speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:  self.player.vy += self.player.speed

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

        # Condição de Vitória (Se o valor do chão for 2, é a saída)
        if tile_value == 2:
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

            self.handle_input()
            
            if not self.game_over and not self.won:
                self.player.update(dt, self.maze.wall_rects)
                self.enemy.update(dt, self.player, self.maze)
                self.check_conditions()

            sw, sh = self.screen.get_size()
            target_x = self.player.x - sw / 2
            target_y = self.player.y - sh / 2
            self.camera.x += (target_x - self.camera.x) * 0.08
            self.camera.y += (target_y - self.camera.y) * 0.08

            self.screen.fill(C_BG)
            self.maze.draw(self.screen, self.camera, self.time)
            
            entities = [self.player, self.enemy]
            entities.sort(key=lambda e: e.y)
            for e in entities:
                e.draw(self.screen, self.camera)
            if not self.won:
                self.fog.draw(self.screen, self.player.x, self.player.y, self.camera, self.time, self.maze)

            if self.game_over:
                self.draw_ui_overlay("VOCÊ FOI PEGO!", (255, 50, 50), (60, 0, 0, 180))
            elif self.won:
                self.draw_ui_overlay("VOCÊ ESCAPOU!", C_EXIT, (10, 30, 10, 180))

            pygame.display.flip()

if __name__ == "__main__":
    Game().run()