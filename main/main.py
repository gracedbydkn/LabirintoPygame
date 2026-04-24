import pygame
import sys
import math
import random

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
SCREEN_W, SCREEN_H = 800, 600
TILE  = 32
FPS   = 60

# Fog-of-war / lighting
FOV_RADIUS    = 180   # pixel radius of full-bright area
FOV_RAYS      = 360   # number of shadow rays (higher = smoother)
FOV_SOFT_EDGE = 60    # pixels of fade at edge

# Colors
C_BG         = (4,  3,  10)
C_WALL_DARK  = (30, 25, 60)
C_WALL_MID   = (55, 45,100)
C_WALL_LIGHT = (90, 75,150)
C_WALL_EDGE  = (120,100,190)
C_FLOOR_DARK = (18, 16, 35)
C_FLOOR_MID  = (25, 22, 48)
C_FLOOR_DOT  = (35, 30, 65)
C_PLAYER     = (80,200,255)
C_PLAYER_EYE = (255,255,255)
C_PLAYER_PUP = (10, 10, 40)
C_PLAYER_GLOW= (40,120,200)
C_EXIT       = (255,215,  0)
C_EXIT_GLOW  = (255,180,  0)
C_HUD_TEXT   = (200,180,255)
C_WIN_TEXT   = (255,215,  0)

# ─────────────────────────────────────────────
#  MAZE MAP  (1=wall, 0=floor, 2=exit)
# ─────────────────────────────────────────────
MAZE_DATA = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,0,1,1,1,0,1,0,1,1,1,1,1,0,1,1,1,0,0,0,1],
    [1,0,1,0,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1],
    [1,0,1,0,1,1,1,0,1,1,1,1,1,0,1,0,1,1,1,0,1,0,0,0,1],
    [1,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,0,1,0,1,1,1,1,1,1,1,0,1,0,1,1,1,1,1,1,1,0,1],
    [1,0,0,0,1,0,1,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,1,0,1],
    [1,0,1,1,1,0,1,0,1,1,1,0,1,0,1,1,1,1,1,1,1,0,1,0,1],
    [1,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
    [1,1,1,1,1,0,1,0,1,0,1,1,1,1,1,1,1,0,1,0,1,1,1,0,1],
    [1,0,0,0,1,0,0,0,1,0,1,0,0,0,0,0,1,0,1,0,0,0,1,0,1],
    [1,0,1,0,1,1,1,1,1,0,1,0,1,1,1,0,1,0,1,1,1,0,1,0,1],
    [1,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,1],
    [1,0,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,0,1],
    [1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1],
    [1,0,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1,0,1,1,1,1,1,0,1],
    [1,0,1,0,0,0,0,0,1,0,1,0,0,0,1,0,1,0,0,0,0,0,1,0,1],
    [1,0,1,0,1,1,1,0,1,0,1,0,1,0,0,0,1,1,1,1,1,0,1,0,1],
    [1,0,0,0,1,0,0,0,0,0,1,0,1,1,1,1,0,0,0,0,1,0,0,0,1],
    [1,0,1,1,1,0,1,1,1,1,1,0,0,0,0,0,0,1,1,0,1,1,1,0,1],
    [1,0,0,0,0,0,1,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,1],
    [1,1,1,0,1,1,1,0,1,1,1,0,1,0,0,0,0,0,1,1,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,2,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

MAP_ROWS = len(MAZE_DATA)
MAP_COLS = len(MAZE_DATA[0])
MAP_W    = MAP_COLS * TILE
MAP_H    = MAP_ROWS * TILE


# ─────────────────────────────────────────────
#  SPRITE HELPERS
# ─────────────────────────────────────────────
def make_wall_tile():
    surf = pygame.Surface((TILE, TILE))
    surf.fill(C_WALL_DARK)
    for i in range(TILE):
        t = i / TILE
        r = int(C_WALL_DARK[0] + (C_WALL_MID[0]-C_WALL_DARK[0]) * t)
        g = int(C_WALL_DARK[1] + (C_WALL_MID[1]-C_WALL_DARK[1]) * t)
        b = int(C_WALL_DARK[2] + (C_WALL_MID[2]-C_WALL_DARK[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, i), (TILE-1, i))
    pygame.draw.rect(surf, C_WALL_LIGHT, (2, 2, TILE-4, TILE-4), 1)
    pygame.draw.line(surf, C_WALL_EDGE, (4, 4), (TILE//2, TILE//2), 1)
    pygame.draw.line(surf, C_WALL_MID,  (TILE//2, 4), (TILE-6, TILE-6), 1)
    pygame.draw.line(surf, C_WALL_EDGE, (0, 0), (TILE-1, 0))
    pygame.draw.line(surf, C_WALL_EDGE, (0, 0), (0, TILE-1))
    pygame.draw.line(surf, C_WALL_DARK, (0, TILE-1), (TILE-1, TILE-1))
    pygame.draw.line(surf, C_WALL_DARK, (TILE-1, 0), (TILE-1, TILE-1))
    return surf

def make_floor_tile():
    surf = pygame.Surface((TILE, TILE))
    surf.fill(C_FLOOR_DARK)
    for ry in range(0, TILE, 8):
        for rx in range(0, TILE, 8):
            if (rx//8 + ry//8) % 2 == 0:
                pygame.draw.rect(surf, C_FLOOR_MID, (rx, ry, 8, 8))
    pygame.draw.circle(surf, C_FLOOR_DOT, (TILE//2, TILE//2), 1)
    return surf

def make_exit_tile():
    surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    surf.fill((0,0,0,0))
    pygame.draw.rect(surf, (*C_EXIT_GLOW, 80), (2, 2, TILE-4, TILE-4), border_radius=4)
    pygame.draw.rect(surf, (*C_EXIT, 200),     (4, 4, TILE-8, TILE-8), border_radius=3)
    pygame.draw.polygon(surf, (255,255,200), [
        (TILE//2, 6), (TILE-6, TILE-6), (6, TILE-6)
    ])
    return surf


# ─────────────────────────────────────────────
#  FOG OF WAR  (shadow-casting raycaster)
# ─────────────────────────────────────────────
class FogOfWar:
    def __init__(self):
        self._grad_cache = {}

    @staticmethod
    def _cast_ray(ox, oy, angle, max_dist):
        dx = math.cos(angle)
        dy = math.sin(angle)
        step = TILE // 4
        dist = 0.0
        while dist < max_dist:
            dist += step
            tx = int((ox + dx * dist) // TILE)
            ty = int((oy + dy * dist) // TILE)
            if tx < 0 or ty < 0 or tx >= MAP_COLS or ty >= MAP_ROWS:
                return dist
            if MAZE_DATA[ty][tx] == 1:
                return max(0.0, dist - step * 0.5)
        return max_dist

    def _build_light_polygon(self, px, py, camera):
        """Screen-space polygon of the visible cone."""
        cx = px - camera.x
        cy = py - camera.y
        max_r = FOV_RADIUS + FOV_SOFT_EDGE
        pts = []
        for i in range(FOV_RAYS):
            angle = (i / FOV_RAYS) * math.tau
            dist  = self._cast_ray(px, py, angle, max_r)
            pts.append((int(cx + math.cos(angle) * dist),
                        int(cy + math.sin(angle) * dist)))
        return pts

    def _get_gradient(self, radius):
        if radius in self._grad_cache:
            return self._grad_cache[radius]
        size = radius * 2 + 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        c = radius + 1
        for r in range(radius, 0, -1):
            ratio = r / radius
            t     = ratio * ratio * (3 - 2 * ratio)   # smoothstep
            alpha = int(255 * t)
            pygame.draw.circle(surf, (0, 0, 0, alpha), (c, c), r)
        self._grad_cache[radius] = surf
        return surf

    def draw(self, surface, player_x, player_y, camera, time):
        w, h = surface.get_size()

        # Full-dark overlay
        fog = pygame.Surface((w, h), pygame.SRCALPHA)
        fog.fill((0, 0, 0, 255))

        # Cut out lit polygon
        pts = self._build_light_polygon(player_x, player_y, camera)
        if len(pts) >= 3:
            pygame.draw.polygon(fog, (0, 0, 0, 0), pts)

        # Soft radial gradient for edge fade
        cx_s = int(player_x - camera.x)
        cy_s = int(player_y - camera.y)
        grad = self._get_gradient(FOV_RADIUS + FOV_SOFT_EDGE)
        fog.blit(grad, grad.get_rect(center=(cx_s, cy_s)),
                 special_flags=pygame.BLEND_RGBA_MAX)

        # Subtle flicker
        flicker = int(3 * math.sin(time * 7.3) + 2 * math.sin(time * 13.1))
        fog.set_alpha(max(0, min(255, 238 + flicker)))

        surface.blit(fog, (0, 0))


# ─────────────────────────────────────────────
#  MAP
# ─────────────────────────────────────────────
class Maze:
    def __init__(self):
        self.data       = MAZE_DATA
        self.wall_surf  = make_wall_tile()
        self.floor_surf = make_floor_tile()
        self.exit_surf  = make_exit_tile()
        self.wall_rects = []
        self.exit_rect  = None
        for row in range(MAP_ROWS):
            for col in range(MAP_COLS):
                if self.data[row][col] == 1:
                    self.wall_rects.append(pygame.Rect(col*TILE, row*TILE, TILE, TILE))
                elif self.data[row][col] == 2:
                    self.exit_rect = pygame.Rect(col*TILE, row*TILE, TILE, TILE)

    def draw(self, surface, camera):
        cx = int(camera.x); cy = int(camera.y)
        c0 = max(0, cx//TILE);        r0 = max(0, cy//TILE)
        c1 = min(MAP_COLS, c0 + SCREEN_W//TILE + 2)
        r1 = min(MAP_ROWS, r0 + SCREEN_H//TILE + 2)
        for row in range(r0, r1):
            for col in range(c0, c1):
                sx = col*TILE - cx; sy = row*TILE - cy
                v  = self.data[row][col]
                if v == 1:
                    surface.blit(self.wall_surf,  (sx, sy))
                elif v == 2:
                    surface.blit(self.floor_surf, (sx, sy))
                    surface.blit(self.exit_surf,  (sx, sy))
                else:
                    surface.blit(self.floor_surf, (sx, sy))


# ─────────────────────────────────────────────
#  PLAYER
# ─────────────────────────────────────────────
class Player:
    SPEED     = 120
    RADIUS    = 11
    BOB_AMP   = 2
    BOB_SPEED = 8

    def __init__(self, x, y):
        self.x = float(x); self.y = float(y)
        self.vx = self.vy = 0.0
        self.facing = pygame.Vector2(1, 0)
        self.bob_t  = 0.0
        self.moving = False
        self.step_count = 0
        self._glow = pygame.Surface((TILE*2, TILE*2), pygame.SRCALPHA)
        c = TILE
        for r in range(TILE, 2, -1):
            a = int(60 * (1 - r / TILE))
            pygame.draw.circle(self._glow, (*C_PLAYER_GLOW, a), (c, c), r)

    def _draw_frame(self, surface, sx, sy, bob):
        c   = self.RADIUS
        tmp = pygame.Surface((c*2+2, c*2+6), pygame.SRCALPHA)
        tc  = (c+1, c+1)
        pygame.draw.ellipse(tmp, (0,0,0,60), (2, c+4, c*2-2, c//2))
        pygame.draw.circle(tmp, C_PLAYER_GLOW, tc, c+1)
        pygame.draw.circle(tmp, C_PLAYER,      tc, c)
        fx, fy = self.facing.x, self.facing.y
        for sign in (-1, 1):
            ex = int(tc[0] + fx*5 + sign*(-fy)*4)
            ey = int(tc[1] + fy*5 + sign*fx*4)
            pygame.draw.circle(tmp, C_PLAYER_EYE, (ex, ey), 3)
            pygame.draw.circle(tmp, C_PLAYER_PUP, (ex+int(fx), ey+int(fy)), 2)
        pygame.draw.circle(tmp, (200,230,255,180), (tc[0]-4, tc[1]-4), 3)
        surface.blit(tmp, (sx - tmp.get_width()//2,
                           sy - tmp.get_height()//2 + int(bob)))

    def handle_input(self, keys):
        self.vx = self.vy = 0.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  self.vx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.vx += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:    self.vy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  self.vy += 1
        if self.vx or self.vy:
            v = pygame.Vector2(self.vx, self.vy).normalize()
            self.vx, self.vy = v.x * self.SPEED, v.y * self.SPEED
            self.facing = pygame.Vector2(self.vx, self.vy).normalize()
            self.moving = True
        else:
            self.moving = False

    def _resolve(self, walls):
        r  = self.RADIUS
        pr = pygame.Rect(self.x-r, self.y-r, r*2, r*2)
        for wr in walls:
            if not pr.colliderect(wr): continue
            ol = pr.right  - wr.left;  or_ = wr.right  - pr.left
            ot = pr.bottom - wr.top;   ob  = wr.bottom - pr.top
            if min(ol, or_) < min(ot, ob):
                self.x -= ol if ol < or_ else -or_
            else:
                self.y -= ot if ot < ob  else -ob
            pr = pygame.Rect(self.x-r, self.y-r, r*2, r*2)

    def update(self, dt, walls):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self._resolve(walls)
        if self.moving:
            self.bob_t += dt * self.BOB_SPEED
            self.step_count += 1
        else:
            self.bob_t *= 0.9

    def draw(self, surface, camera):
        sx  = int(self.x - camera.x)
        sy  = int(self.y - camera.y)
        bob = math.sin(self.bob_t) * self.BOB_AMP if self.moving else 0
        surface.blit(self._glow, (sx-TILE, sy-TILE),
                     special_flags=pygame.BLEND_RGBA_ADD)
        self._draw_frame(surface, sx, sy, bob)

    @property
    def rect(self):
        r = self.RADIUS
        return pygame.Rect(self.x-r, self.y-r, r*2, r*2)


# ─────────────────────────────────────────────
#  GAME
# ─────────────────────────────────────────────
class Game:
    def __init__(self):
        pygame.init()
        self.screen  = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Pixel Maze  •  WASD / Arrows to move")
        self.clock   = pygame.time.Clock()
        self.font_lg = pygame.font.SysFont("monospace", 40, bold=True)
        self.font_sm = pygame.font.SysFont("monospace", 18)
        self.maze    = Maze()
        self.fog     = FogOfWar()
        self.player  = Player(1*TILE + TILE//2, 1*TILE + TILE//2)
        self.camera  = pygame.Vector2(0, 0)
        self.won       = False
        self.win_timer = 0.0
        self.particles = []
        self.time      = 0.0

    def _update_camera(self):
        tx = max(0, min(self.player.x - SCREEN_W//2, MAP_W - SCREEN_W))
        ty = max(0, min(self.player.y - SCREEN_H//2, MAP_H - SCREEN_H))
        self.camera.x += (tx - self.camera.x) * 0.12
        self.camera.y += (ty - self.camera.y) * 0.12

    def _spawn_particles(self):
        for _ in range(60):
            a = random.uniform(0, math.tau)
            s = random.uniform(30, 180)
            self.particles.append({
                "x": self.player.x, "y": self.player.y,
                "vx": math.cos(a)*s, "vy": math.sin(a)*s,
                "life": random.uniform(0.5, 1.8), "max_life": 1.8,
                "color": random.choice([C_EXIT, C_PLAYER, (255,255,255)])
            })

    def _update_particles(self, dt):
        for p in self.particles[:]:
            p["x"] += p["vx"]*dt; p["y"] += p["vy"]*dt
            p["vy"] += 80*dt;     p["life"] -= dt
            if p["life"] <= 0: self.particles.remove(p)

    def _draw_particles(self):
        for p in self.particles:
            alpha = max(0, int(255 * p["life"] / p["max_life"]))
            sx = int(p["x"] - self.camera.x)
            sy = int(p["y"] - self.camera.y)
            r  = max(1, int(4 * p["life"] / p["max_life"]))
            tmp = pygame.Surface((r*2+1, r*2+1), pygame.SRCALPHA)
            pygame.draw.circle(tmp, (*p["color"][:3], alpha), (r,r), r)
            self.screen.blit(tmp, (sx-r, sy-r))

    def _draw_exit_glow(self):
        if not self.maze.exit_rect: return
        er   = self.maze.exit_rect
        sx   = er.x - int(self.camera.x)
        sy   = er.y - int(self.camera.y)
        pulse = 0.5 + 0.5 * math.sin(self.time * 3.0)
        rs   = int(TILE * 0.9 + pulse * 8)
        glow = pygame.Surface((rs*2, rs*2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*C_EXIT_GLOW, int(80*pulse)), (rs,rs), rs)
        self.screen.blit(glow, (sx+TILE//2-rs, sy+TILE//2-rs),
                         special_flags=pygame.BLEND_RGBA_ADD)

    def _draw_hud(self):
        label = self.font_sm.render(f"Steps: {self.player.step_count // 10}",
                                    True, C_HUD_TEXT)
        self.screen.blit(label, (10, 10))
        hint = self.font_sm.render(
            "WASD / ↑↓←→  Move  •  Find the ★ exit", True, C_HUD_TEXT)
        self.screen.blit(hint, (10, SCREEN_H - 28))

    def _draw_win_screen(self):
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((5, 4, 12, min(200, int(200 * self.win_timer / 1.5))))
        self.screen.blit(ov, (0, 0))
        if self.win_timer > 0.4:
            t1 = self.font_lg.render("YOU ESCAPED!", True, C_WIN_TEXT)
            t2 = self.font_sm.render("R = restart  •  ESC = quit", True, C_HUD_TEXT)
            cx, cy = SCREEN_W//2, SCREEN_H//2
            self.screen.blit(t1, t1.get_rect(center=(cx, cy-20)))
            self.screen.blit(t2, t2.get_rect(center=(cx, cy+30)))

    def _reset(self):
        self.player    = Player(1*TILE + TILE//2, 1*TILE + TILE//2)
        self.won       = False
        self.win_timer = 0.0
        self.particles = []
        self.time      = 0.0

    def run(self):
        while True:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            self.time += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()
                    if event.key == pygame.K_r:
                        self._reset()

            keys = pygame.key.get_pressed()
            if not self.won:
                self.player.handle_input(keys)
                self.player.update(dt, self.maze.wall_rects)
                self._update_camera()
                if (self.maze.exit_rect and
                        self.player.rect.colliderect(self.maze.exit_rect)):
                    self.won = True
                    self._spawn_particles()
            else:
                self.win_timer += dt
                self._update_particles(dt)
                self._update_camera()

            # ── DRAW ──────────────────────────────
            self.screen.fill(C_BG)

            # 1. World tiles
            self.maze.draw(self.screen, self.camera)
            self._draw_exit_glow()

            # 2. Player character
            if not self.won or self.win_timer < 0.8:
                self.player.draw(self.screen, self.camera)

            # 3. Fog of war overlay
            if not self.won:
                self.fog.draw(self.screen,
                              self.player.x, self.player.y,
                              self.camera, self.time)
            else:
                # gradually lift the fog on win
                reveal = min(1.0, self.win_timer / 1.2)
                if reveal < 1.0:
                    tmp = pygame.Surface((SCREEN_W, SCREEN_H))
                    tmp.fill((0, 0, 0))
                    tmp.set_alpha(int(255 * (1.0 - reveal)))
                    self.screen.blit(tmp, (0, 0))

            # 4. Particles (above fog)
            self._draw_particles()

            # 5. HUD / win screen
            self._draw_hud()
            if self.won:
                self._draw_win_screen()

            pygame.display.flip()


if __name__ == "__main__":
    Game().run()