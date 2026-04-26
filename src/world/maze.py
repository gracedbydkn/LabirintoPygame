# src/world/maze.py
import pygame
import pytmx

class Maze:
    def __init__(self, tmx_file, scale_factor=4):
        self.tmx_data = pytmx.load_pygame(tmx_file)
        self.scale = scale_factor
        self.tile_size = self.tmx_data.tilewidth * self.scale
        
        self.cols = self.tmx_data.width
        self.rows = self.tmx_data.height
        self.map_w = self.cols * self.tile_size
        self.map_h = self.rows * self.tile_size
        
        self.wall_rects = []
        self.matrix = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.map_surface = pygame.Surface((self.map_w, self.map_h))
        self.map_surface.fill((4, 3, 10))
        self._build_map()

    def _build_map(self):
        for layer_index, layer in enumerate(self.tmx_data.visible_layers):
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile_img = self.tmx_data.get_tile_image_by_gid(gid)
                    props = self.tmx_data.get_tile_properties_by_gid(gid)
                    
                    if tile_img:
                        tile_img = pygame.transform.scale(tile_img, (self.tile_size, self.tile_size))
                        px = x * self.tile_size
                        py = y * self.tile_size
                        self.map_surface.blit(tile_img, (px, py))
                        
                        if layer_index == 1:
                            self.matrix[y][x] = 1
                            self.wall_rects.append(pygame.Rect(px, py, self.tile_size, self.tile_size))
                            
                        if props:
                            if props.get("Tipo") == "exit":
                                self.matrix[y][x] = 2
                            elif props.get("Tipo") == "hide":
                                self.matrix[y][x] = 3

    def get_tile_value(self, grid_x, grid_y):
        if 0 <= grid_x < self.cols and 0 <= grid_y < self.rows:
            return self.matrix[grid_y][grid_x]
        return 1

    def draw(self, surface, camera, time=0):
        surface.blit(self.map_surface, (-camera.x, -camera.y))