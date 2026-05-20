# src/world/maze.py
import pygame
import pytmx  # Biblioteca para carregar mapas no formato .tmx (editor Tiled)

class Maze:
    def __init__(self, tmx_file, scale_factor=4):
        # Carrega o arquivo de mapa .tmx convertendo os tiles para superfícies pygame
        self.tmx_data = pytmx.load_pygame(tmx_file)

        # Fator de escala: multiplica o tamanho original dos tiles (ex: 16px → 64px)
        self.scale = scale_factor
        self.tile_size = self.tmx_data.tilewidth * self.scale

        # Dimensões do mapa em número de tiles
        self.cols = self.tmx_data.width
        self.rows = self.tmx_data.height

        # Dimensões totais do mapa em pixels
        self.map_w = self.cols * self.tile_size
        self.map_h = self.rows * self.tile_size

        # Lista de retângulos das paredes — usada para detecção de colisão
        self.wall_rects = []

        # Matriz lógica do mapa: 0=chão, 1=parede, 2=saída, 3=esconderijo
        self.matrix = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        # Superfície pré-renderizada do mapa — desenhada uma vez e reutilizada
        self.map_surface = pygame.Surface((self.map_w, self.map_h))
        self.map_surface.fill((4, 3, 10))  # Fundo com a cor C_BG do config

        # Constrói o mapa a partir dos dados do .tmx
        self._build_map()

    def _build_map(self):
        """Percorre todas as camadas visíveis do .tmx, desenha os tiles na
        map_surface e preenche a matrix lógica com os tipos de cada célula."""
        for layer_index, layer in enumerate(self.tmx_data.visible_layers):
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    # Obtém a imagem e as propriedades do tile pelo seu ID global (gid)
                    tile_img = self.tmx_data.get_tile_image_by_gid(gid)
                    props    = self.tmx_data.get_tile_properties_by_gid(gid)

                    if tile_img:
                        # Redimensiona o tile para o tamanho escalado
                        tile_img = pygame.transform.scale(tile_img, (self.tile_size, self.tile_size))

                        # Calcula a posição em pixels na superfície do mapa
                        px = x * self.tile_size
                        py = y * self.tile_size
                        self.map_surface.blit(tile_img, (px, py))

                        # Camada 1 é reservada para paredes (convenção do projeto)
                        if layer_index == 1:
                            self.matrix[y][x] = 1  # Marca como parede na matrix
                            # Adiciona rect de colisão para essa parede
                            self.wall_rects.append(pygame.Rect(px, py, self.tile_size, self.tile_size))

                        # Lê propriedades customizadas definidas no editor Tiled
                        if props:
                            if props.get("Tipo") == "exit":
                                self.matrix[y][x] = 2   # Saída do labirinto
                            elif props.get("Tipo") == "hide":
                                self.matrix[y][x] = 3   # Ponto de esconderijo

    def get_tile_value(self, grid_x, grid_y):
        """Retorna o valor lógico de uma célula do grid (0, 1, 2 ou 3).
        Retorna 1 (parede) para posições fora dos limites do mapa."""
        if 0 <= grid_x < self.cols and 0 <= grid_y < self.rows:
            return self.matrix[grid_y][grid_x]
        return 1  # Fora do mapa é tratado como parede

    def draw(self, surface, camera, time=0):
        """Desenha a map_surface pré-renderizada na tela, aplicando o offset da câmera.
        Por ser pré-renderizada, essa operação é muito eficiente a cada frame."""
        surface.blit(self.map_surface, (-camera.x, -camera.y))