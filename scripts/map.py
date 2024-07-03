import pygame

from copy import deepcopy
from typing import Literal, NamedTuple, TYPE_CHECKING
import random

from scripts.tile import Tile
from scripts.sprite import SpriteGroup
import scripts.utils as utils

if TYPE_CHECKING:
    from scripts.game import Game


class Map:
    def __init__(self, graphics: dict[str, dict | list], tile_size: int) -> None:
        """
        Representa o mapa do jogo.
        Contem e gerencia um grupo de Tiles.

        Parameters
        ----------
        graphics : dict
            Gráficos a serem utilizados pelas tiles do mapa.
        tile_size : int
            Tamanho das tiles do mapa.
        """
        # --- Controle Interno --- #
        # A criação de tiles depende de uma estrutura interna assumida para __graphics.
        # Caso o mapa esteja gerando com graficos errados, verifique a estrutura do dict
        # comparado com as configurações no método _place_tile()
        self.__graphics = graphics
        self.__WALL: str = "##"
        self.__AIR: str = "  "
        self.__HOLE: str = "**"

        # --- Atributos do mapa --- #
        self.__size: tuple[int, int] = (0, 0)
        self.__border_size: int = 2  # O tamanho da borda tem que ser par
        self.__tile_size: int = tile_size

        # --- Tiles --- #
        self.__foreground_tiles: SpriteGroup[Tile] = SpriteGroup()
        self.__background_tiles: SpriteGroup[Tile] = SpriteGroup()
        self.__matrix_foreground: list[list[Tile | None]] = []
        self.__matrix_background: list[list[Tile | None]] = []

        self.generate()

    def get_tile(
        self,
        pos: tuple[int, int],
        plane: Literal["background", "foreground"] = "foreground",
    ) -> Tile | None:
        """
        Retorna a tile em uma posição específica da grid do mapa.

        Parameters
        ----------
        pos : tuple[int, int]
            Índice da tile no mapa (x, y)
        plane : str, "background" or "foreground", optional
            Em qual plano procurar pela tile, by default "foreground"

        Returns
        -------
        Tile | None
            Tile encontrada, None caso não haja tile na posição

        Raises
        ------
        IndexError
            "pos" deve ser um índice válido dentro do mapa
        """
        if not utils.is_within_bounds(pos[0], pos[1], self.width, self.height):
            raise IndexError(
                f"Posição: {pos} não está dentro de Map: {(self.width - 1, self.height - 1)}"
            )

        tile: Tile | None = None
        if plane == "foreground":
            tile = self.__matrix_foreground[pos[1]][pos[0]]
        else:
            tile = self.__matrix_background[pos[1]][pos[0]]
        return tile

    def get_tiles_square(
        self,
        pos: tuple[int, int],
        radius: int | tuple[int, int] = 1,
        plane: Literal["background", "foreground"] = "foreground",
    ) -> set[Tile]:
        """
        Procura por tiles em um raio quadrado em torno de uma posição.

        Parameters
        ----------
        pos : tuple[int, int]
            Centro do quadrado, índice no mapa (x, y)
        radius : int | tuple[int, int], optional
            Raio quadrado, pode ser uma tupla (x, y), by default 1
        plane : str, "background" or "foreground", optional
            Em qual plano procurar pelas tiles, by default "foreground"

        Returns
        -------
        set[Tile]
            Set com as tiles encontradas

        Raises
        ------
        IndexError
            A posição tem que estar dentro do mapa
        """
        if not utils.is_within_bounds(pos[0], pos[1], self.width, self.height):
            raise IndexError(
                f"Posição: {pos} não está dentro de Map: {self.width - 1, self.height - 1}"
            )

        # --- Setup --- #
        # Obtem o raio
        if not isinstance(radius, tuple):
            radius = (radius, radius)
        x_min = int(pos[0] - radius[0])
        x_max = int((pos[0] + 1) + radius[0])
        y_min = int(pos[1] - radius[1])
        y_max = int(pos[1] + 1) + radius[1]

        # --- Procura as Tiles --- #
        tiles: set[Tile] = set()

        for x in range(x_min, x_max):
            for y in range(y_min, y_max):
                if utils.is_within_bounds(x, y, self.width, self.height):
                    tile = self.get_tile((x, y), plane)
                    if isinstance(tile, Tile):
                        tiles.add(tile)
        return tiles

    def place_tile(
        self,
        pos: tuple[int, int],
        tile_code: "TileCode",
        *groups: SpriteGroup,
        plane: Literal["background", "foreground"] = "foreground",
        visible: bool = True,
        collidable: bool = False,
    ) -> None:
        """
        Coloca uma tile no mapa.

        Parameters
        ----------
        pos : tuple[int, int]
            Índice da tile (x, y)
        tile_code : TileCode
            Tupla contendo (código da tile: str, variação: int)
            Se a variação for um número inválido, uma aleatória é escolhida
        *groups : SpriteGroup
            Todos os grupos que a tile deve pertencer
        plane : str, "background" or "foreground", optional
            Em qual plano do mapa colocar a tile, by default "foreground"
        visible : bool, optional
            Se a tile é visível, by default True
        collidable : bool, optional
            Se a tile tem colisão, by default False

        Raises
        ------
        IndexError
            "pos" deve ser um índice válido dentro do mapa
        """
        if not utils.is_within_bounds(pos[0], pos[1], self.width, self.height):
            raise IndexError(
                f"Posição: {pos} não está dentro de Map: {self.width - 1, self.height - 1}"
            )

        # --- Controle --- #
        tile_inflate: dict[str, tuple[int, int]] = {
            "wall": (0, -8),
            "wall_top": (0, -8),
            "stone": (-4, -4),
        }
        tile_move: dict[str, tuple[int, int]] = {"wall": (0, -10), "wall_top": (0, 4)}

        # --- Decidindo a Tile --- #
        pixel_pos = pygame.Vector2(
            (pos[0] * self.__tile_size), pos[1] * self.__tile_size
        )

        # - Se o tipo da tile for None, a tile não é criada.
        if tile_code.type == "None":
            return

        # - Verifica se o tipo da tile existe
        if tile_code.type not in self.__graphics.keys():
            tile_code = TileCode("None", 0)

        # - Escolhe a imagem da Tile
        if tile_code.variation >= 0 and tile_code.variation < len(
            self.__graphics[tile_code.type]
        ):
            image = self.__graphics[tile_code.type][tile_code.variation]
        else:
            image = random.choice(self.__graphics[tile_code.type])

        # --- Criando a Tile --- #
        created_tile = Tile(
            self,
            pixel_pos,
            image,
            tile_inflate.get(tile_code.type, (0, 0)),
            tile_move.get(tile_code.type, (0, 0)),
            *groups,
            visible=visible,
            collidable=collidable,
        )

        if plane == "foreground":
            self.__matrix_foreground[pos[1]][pos[0]] = created_tile
            created_tile.add_to(self.__foreground_tiles)
        else:
            self.__matrix_background[pos[1]][pos[0]] = created_tile
            created_tile.add_to(self.__background_tiles)

    def remove_tile(
        self,
        pos: tuple[int, int],
        plane: Literal["background", "foreground"] = "foreground",
    ) -> None:
        """
        Deleta uma tile do mapa.

        Parameters
        ----------
        pos : tuple[int, int]
            Índice da tile (x, y)
        plane : str, "background" or "foreground", optional
            De qual plano do mapa remover a tile, by default "foreground"

        Raises
        ------
        IndexError
            A posição tem que estar dentro do mapa
        """
        if not utils.is_within_bounds(pos[0], pos[1], self.width, self.height):
            raise IndexError(
                f"Posição: {pos} não está dentro de Map: {self.width - 1, self.height - 1}"
            )

        tile = self.get_tile(pos, plane)
        if tile != None:
            assert tile is not None
            if plane == "foreground":
                tile.kill()
                self.__matrix_foreground[pos[0]][pos[1]] = None
            else:
                tile.kill()
                self.__matrix_background[pos[0]][pos[1]] = None

    def clear(self) -> None:
        self.foreground_tiles.empty()
        self.background_tiles.empty()
        self.__matrix_foreground.clear()
        self.__matrix_background.clear()

    def generate(self) -> None:
        """
        Limpa o mapa atual e gera um novo mapa aleatoriamente.
        """
        # --- Setup --- #
        self.clear()
        transparent_tiles: set = set("stone")

        # O tamanho do mapa TEM QUE SER PAR
        self.__size = (
            31 * 2,  # linhas (y)
            31 * 2,  # colunas (x)
        )
        self.__matrix_background = [[None] * self.width for _ in range(self.height)]
        self.__matrix_foreground = [[None] * self.width for _ in range(self.height)]

        # --- Gera os labirintos --- #
        foreground_maze = self.__create_maze()
        foreground_maze = self.__smooth_maze(foreground_maze, 3, 6, 10, 4, 0)
        foreground_maze = self.__smooth_maze(foreground_maze, 5, 7, 10, 3, 0)

        background_maze = deepcopy(foreground_maze)
        background_maze = self.__smooth_maze(background_maze, 3, 0, 4, 6, 2)

        # --- Constroi o mapa --- #
        blueprint_background, blueprint_foreground = self.__tilemap_maze(
            background_maze, foreground_maze
        )

        for y, line in enumerate(blueprint_foreground):
            for x, tile in enumerate(line):
                if tile.type != "None":
                    self.place_tile((x, y), tile, plane="foreground", collidable=True)
                    # Caso a tile colocada seja transparente
                    if tile.type == "stone":
                        self.place_tile(
                            (x, y), blueprint_background[y][x], plane="background"
                        )
                else:
                    self.place_tile(
                        (x, y), blueprint_background[y][x], plane="background"
                    )

    def __create_maze(self) -> list[list]:
        """
        Cria um labirinto em uma matriz de largura e altura pares.
        O algoritmo utilizado é o Depth-First Search aleatório.
        Tiles geradas serão do tipo "self.__WALL" e "self.__AIR".

        Returns
        -------
        list[list]
            Labirinto gerado.

        Raises
        ------
        ValueError
            Ambas dimensões de "self.__size" devem ser números pares.
            O tamanho da borda do mapa deve ser um número par.
        """
        if self.__size[0] % 2 != 0 or self.__size[1] % 2 != 0:
            raise ValueError(
                "Ambas dimensões do tamanho do mapa devem ser números pares."
            )
        if self.__border_size % 2 != 0:
            raise ValueError("O tamanho da borda do mapa deve ser par.")

        # --- Setup --- #
        width, height = int(self.width / 2), int(self.height / 2)
        maze = [[self.__WALL] * width for _ in range(height)]
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        def __has_unvisited_neighbors(pos: tuple[int, int]) -> bool:
            """
            Verifica se uma coordenada no labirinto tem vizinhos não visitados

            Parameters
            ----------
            pos: tuple[int, int]
                coordenada (x, y)

            Returns
            -------
            bool
            """
            for dy, dx in directions:
                nx, ny = pos[0] + (dx * 2), pos[1] + (dy * 2)
                if (
                    utils.is_within_bounds(nx, ny, width, height)
                    and maze[ny][nx] == self.__WALL
                ):
                    return True
            return False

        # --- Criando o Labirinto --- #
        # Ponto de inicio
        sx, sy = int(width / 2), int(height / 2)
        maze[sy][sx] = self.__AIR

        stack = [(sx, sy)]
        while stack:
            cx, cy = stack[-1]
            if __has_unvisited_neighbors((cx, cy)):
                maze[cy][cx] = self.__AIR
                random.shuffle(directions)
                for dy, dx in directions:
                    nx, ny = cx + (dx * 2), cy + (dy * 2)
                    if (
                        utils.is_within_bounds(nx, ny, width, height)
                        and maze[ny][nx] == self.__WALL
                    ):
                        # Quebra a parede entre a celula atual e a nova celula
                        maze[cy + dy][cx + dx] = self.__AIR
                        # Marca a nova celula como HOLE
                        maze[ny][nx] = self.__HOLE
                        stack.append((nx, ny))
                        break
            else:
                stack.pop()
        maze[sy][sx] = self.__HOLE

        # --- Polindo o Labirinto --- #
        # No lugar dos "self.__HOLE" e suas celulas vizinhas é colocado "self.__AIR"
        border = int(self.__border_size / 2)
        adjacent_directions = [
            (0, 1),
            (0, -1),
            (1, 0),
            (1, 1),
            (0, -1),
            (-1, 0),
            (-1, 1),
            (-1, -1),
        ]
        for y, line in enumerate(maze):
            if y < border or y >= (height - border):
                maze[y] = [self.__WALL] * width
                continue
            for x, element in enumerate(line):
                # Fecha as bordas do labirinto com paredes
                if x < border or x >= (width - border):
                    maze[y][x] = self.__WALL
                    continue

                if element == self.__HOLE:
                    for dy, dx in adjacent_directions:
                        nx, ny = x + dx, y + dy
                        if (
                            utils.is_within_bounds(
                                nx - border,
                                ny - border,
                                width - (border * 2),
                                height - (border * 2),
                            )
                            and maze[ny][nx] == self.__WALL
                        ):
                            maze[ny][nx] = self.__AIR
                        maze[y][x] = self.__AIR

        # --- Retornando o Labirinto para o tamanho original --- #
        expand_directions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        final_maze = [[self.__WALL] * (width * 2) for _ in range(height * 2)]
        for y, line in enumerate(maze):
            for x, element in enumerate(line):
                fx, fy = x * 2, y * 2
                for dy, dx in expand_directions:
                    final_maze[fy + dy][fx + dx] = maze[y][x]
        return final_maze

    def __smooth_maze(
        self,
        maze: list[list],
        ammount: int,
        stop_air: int,
        stop_wall: int,
        air_neighbors: int,
        wall_neighbors: int,
    ) -> list[list]:
        """
        Suaviza um labirinto.
        A suavização utiliza um altoritmo celular-automata.

        Parameters
        ----------
        maze : list[list]
            Labirinto
        ammount : int
            Quantas iterações do celular automata
        stop_air : int
            Quanto impedir a expansão do "self.__AIR":
            10 = nunca expande
            0 = sempre expande
        stop_wall : int
            Quanto impedir a expansão do "self.__WALL":
            10 = nunca expande
            0 = sempre expande
        air_neighbors : int
            Quantos vizinhos "self.__AIR" precisa para expandir
        wall_neighbors : int
            Quantos vizinhos "self.__WALL" precisa para expandir

        Returns
        -------
        list[list]
            Labirinto suavizado
        """
        # --- Setup --- #
        adjacent_directions = [
            (0, 1),
            (0, -1),
            (1, 0),
            (1, 1),
            (0, -1),
            (-1, 0),
            (-1, 1),
            (-1, -1),
        ]

        for i in range(ammount):
            temp_maze = deepcopy(maze)
            for y, line in enumerate(maze):
                # Pula as bordas
                if y < self.__border_size or y >= (self.height - self.__border_size):
                    continue
                for x, element in enumerate(line):
                    # Pula as bordas
                    if x < self.__border_size or x >= (self.width - self.__border_size):
                        continue

                    # Conta os vizinhos
                    wall_count = 0
                    air_count = 0
                    for dy, dx in adjacent_directions:
                        nx, ny = x + dx, y + dy
                        if utils.is_within_bounds(nx, ny, self.width, self.height):
                            if maze[ny][nx] == self.__WALL:
                                wall_count += 1
                            elif maze[ny][nx] == self.__AIR:
                                air_count += 1
                        else:
                            wall_count += 1

                    # Modifica o labirinto
                    if (
                        wall_count >= wall_neighbors
                        and element == self.__AIR
                        and random.randint(1, 10) > stop_wall
                    ):
                        temp_maze[y][x] = self.__WALL
                    elif (
                        air_count >= air_neighbors
                        and element == self.__WALL
                        and random.randint(1, 10) > stop_air
                    ):
                        temp_maze[y][x] = self.__AIR
            maze = temp_maze
        return maze

    def __tilemap_maze(
        self, backgorund: list[list], foreground: list[list]
    ) -> tuple[list[list["TileCode"]], list[list["TileCode"]]]:
        """
        Transforma labirintos background e foreground em um tilemap

        Parameters
        ----------
        background : list[list]
            Labirinto do background
        foreground : list[list]
            Labirinto do foreground

        Returns
        -------
        tuple[list[list["TileCode"]], list[list["TileCode"]]]
            Tupla contendo os TileCodes para o background [0] e foreground [1]
        """
        # --- Setup --- #
        neighbor_directions = [
            (0, 1),  # Leste
            (0, -1),  # Oeste
            (1, 0),  # Sul
            (-1, 0),  # Norte
        ]
        background_tilemap = [
            [TileCode("None", 0) for _ in range(self.width)] for _ in range(self.height)
        ]
        foreground_tilemap = [
            [TileCode("None", 0) for _ in range(self.width)] for _ in range(self.height)
        ]

        variations: list[int]
        weights: list[float]

        # --- Conversão --- #
        # - Background
        for y, line in enumerate(backgorund):
            for x, tile in enumerate(line):
                if tile == self.__WALL:
                    variations = [0, 1, 2, 3]
                    weights = [0.45, 0.25, 0.15, 0.15]
                    background_tilemap[y][x] = TileCode(
                        "stone_floor",
                        random.choices(variations, weights=weights, k=1)[0],
                    )
                else:
                    variations = [0, 1, 2, 3, 4, 5]
                    weights = [0.35, 0.35, 0.05, 0.05, 0.1, 0.1]
                    background_tilemap[y][x] = TileCode(
                        "dirt_floor",
                        random.choices(variations, weights=weights, k=1)[0],
                    )

        # - Foreground
        for y, line in enumerate(foreground):
            # Borda por linha
            if y < self.__border_size or y >= (self.height - self.__border_size):
                foreground_tilemap[y] = [
                    TileCode("wall_top", -1) for _ in range(self.width)
                ]
                continue
            for x, tile in enumerate(line):
                # Borda por coluna
                if x < self.__border_size or x >= (self.width - self.__border_size):
                    foreground_tilemap[y][x] = TileCode("wall_top", -1)
                    continue
                elif y == self.__border_size and tile == self.__AIR:
                    foreground_tilemap[y][x] = TileCode("wall", 0)
                    continue

                if tile == self.__WALL:
                    # - Registra os vizinhos da celula
                    # Tiles adjacentes, direções na mesma ordem que neighbor_directions
                    neighbors: list = [None, None, None, None]
                    for i, direction in enumerate(neighbor_directions):
                        nx, ny = x + direction[1], y + direction[0]
                        if utils.is_within_bounds(nx, ny, self.width, self.height):
                            neighbors[i] = foreground[ny][nx]
                    East, West, South, North = neighbors

                    # - Decide a tile
                    if South == self.__WALL:
                        foreground_tilemap[y][x] = TileCode("wall_top", -1)
                    else:
                        if North == self.__AIR:
                            foreground_tilemap[y][x] = TileCode("stone", -1)
                        else:
                            if West == self.__WALL:
                                if East == self.__WALL:
                                    foreground_tilemap[y][x] = TileCode("wall", 0)
                                else:
                                    foreground_tilemap[y][x] = TileCode("wall", 1)
                            else:
                                if East == self.__WALL:
                                    foreground_tilemap[y][x] = TileCode("wall", 2)
                                else:
                                    foreground_tilemap[y][x] = TileCode("wall", 3)

        return (background_tilemap, foreground_tilemap)

    @property
    def size(self) -> tuple[int, int]:
        return self.__size

    @property
    def size_pixels(self) -> tuple[int, int]:
        return (self.__size[0] * self.__tile_size, self.__size[1] * self.__tile_size)

    @property
    def width(self) -> int:
        return self.__size[1]

    @property
    def height(self) -> int:
        return self.__size[0]

    @property
    def tile_size(self) -> int:
        return self.__tile_size

    @property
    def background_tiles(self) -> SpriteGroup:
        return self.__background_tiles

    @property
    def foreground_tiles(self) -> SpriteGroup:
        return self.__foreground_tiles


class TileCode(NamedTuple):
    type: str
    variation: int
