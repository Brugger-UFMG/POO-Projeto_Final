import pygame

from typing import TYPE_CHECKING, Type
import random

from scripts.entity import Entity, EntityManager
from scripts.sprite import Sprite, SpriteGroup
from scripts.tile import Tile
import scripts.utils as utils
from scripts.map import Map
from scripts.player import Player
from scripts.camera import Camera
from scripts.enemies import Enemy, Hornet, Spider, Beetle

if TYPE_CHECKING:
    from scripts.main import Main


class Game:
    def __init__(self, window: pygame.Surface, display: pygame.Surface) -> None:
        """
        Representa o jogo.

        Parameters
        ----------
        window : pygame.Surface
            Janela do jogo.
        display : pygame.Surface
            Display onde renderizar o jogo.
        """
        # --- Setup --- #
        self.__display = display
        self.__window = window
        self.__graphics: dict = utils.load_directory("graphics")

        # --- Objetos do jogo --- #
        self.__map: Map = Map(self.__graphics["tiles"], 16)
        self._player: Player = Player(
            self,
            pygame.Vector2(
                (self.map.size_pixels[0] // 2, self.map.size_pixels[1] // 2)
            ),
            self.__graphics["entities"]["player"][0],
        )
        self._entities: EntityManager = EntityManager()
        self._enemies: EntityManager = EntityManager()
        self._camera: Camera = Camera(self.display, self.map, self._player)

        # --- Outros --- #
        self._score: int = 0
        self._score_cooldown: float = 1.0
        self._score_time: float = 1.0
        self._game_over: bool = False
        self._game_over_time: float = 0

    def run(self, dt: float) -> None:
        """
        Roda um frame do jogo.

        Parameters
        ----------
        dt : float
            Tempo desde o último frame
        """
        # --- Atualiza a lógica interna do jogo --- #
        # Entidades
        if self._player.check_death() == True:
            self._player.image = self.__graphics["tiles"]["None"][0]
            self._game_over = True

            if self._game_over_time <= 255:
                self._game_over_time += dt * 64
            else:
                self._game_over_time = 255

        self._player.update(dt)
        self._entities.update(dt)

        to_add = []
        for entity in self._entities:
            if isinstance(entity, Enemy):
                assert isinstance(entity, Enemy)
                for projectyle in entity.projectyles:
                    to_add.append(projectyle)

        self._entities.add(*to_add)

        enemies_killed = self._enemies.check_deaths()
        self._entities.check_deaths()

        # Pontuação
        if self._game_over == False:
            self._score_time -= dt
            if self._score_time <= 0:
                self._spawn_enemies()
                self._score += 1
                self._score_time = self._score_cooldown

            for enemy in enemies_killed:
                assert isinstance(enemy, Enemy)
                self._score += enemy.value

        # --- Desenha o jogo --- #
        self.__display.fill("Black")
        # Background
        self._camera.render_sprites(self.map.background_tiles)

        # Foreground
        foreground = SpriteGroup[Sprite]()
        for sprites in self.map.foreground_tiles:
            foreground.add(sprites)
        foreground.add(self._player)
        for sprites in self.entities:
            foreground.add(sprites)
        self._camera.render_sprites_y_sorted(foreground)
        foreground.empty()

        # --- Desenha o jogo e a UI na janela --- #
        # Escala o jogo para o tamanho da janela
        self.__window.fill("Black")
        self.__window.blit(
            pygame.transform.scale(
                self.__display, (self.__window.get_width(), self.__window.get_height())
            ),
            (0, 0),
        )
        # --- Desenha a UI --- #
        # Vida e pontos:
        if self._game_over == False:
            score_text = utils.create_outline_text(
                f"Score: {self._score}",
                pygame.Color(255, 255, 255),
                24,
                self.window.get_width() // 2,
                15,
                1,
                pygame.Color(0, 0, 40),
            )

            life_text = utils.create_outline_text(
                f"Life: {self.player.health}",
                pygame.Color(255, 255, 255),
                24,
                self.window.get_width() // 2,
                score_text[1].height + 15,
                1,
                pygame.Color(128, 0, 0),
            )
            self.__window.blit(score_text[0], score_text[1])
            self.__window.blit(life_text[0], life_text[1])

        # Game Over
        else:
            game_over_text = utils.create_outline_text(
                "G a m e  O v e r !",
                pygame.Color(255, 255, 255),
                52,
                self.window.get_width() // 2,
                self.window.get_height() // 2 - self.window.get_height() // 8,
                3,
                pygame.Color(80, 0, 0),
            )

            final_score_text = utils.create_outline_text(
                f"Final Score: {self._score}",
                pygame.Color(255, 255, 255),
                32,
                self.window.get_width() // 2,
                game_over_text[1].y + game_over_text[1].height + 10,
                3,
                pygame.Color(0, 1, 0),
            )
            game_over_text[0].set_alpha(int(self._game_over_time))
            final_score_text[0].set_alpha(int(self._game_over_time))

            self.__window.blit(game_over_text[0], game_over_text[1])
            self.__window.blit(final_score_text[0], final_score_text[1])

    def _spawn_enemies(self) -> None:
        """
        Procura por um lugar apropriado e cria um inimigo.
        """
        unavailable_tiles = self.map.get_tiles_square(
            self.player.tile_pos, 10, "background"
        )
        available_tiles: set[Tile] = (
            set(self.map.background_tiles.items()) - unavailable_tiles
        )

        while True:
            tile: Tile = random.choice(list(available_tiles))
            if self.map.get_tile(tile.tile_pos) == None:
                pos = pygame.Vector2(tile.pos)
                break
            else:
                available_tiles.remove(tile)

        enemy_types: list[Type] = [Hornet, Beetle, Spider]
        weights = [0.7, 0.05, 0.25]
        enemy = random.choices(enemy_types, weights=weights, k=1)[0]
        self._enemies.add(enemy(self, pos, self._entities))

    @property
    def graphics(self) -> dict:
        return self.__graphics

    @property
    def display(self) -> pygame.Surface:
        return self.__display

    @property
    def window(self) -> pygame.Surface:
        return self.__window

    @property
    def map(self) -> Map:
        return self.__map

    @property
    def camera(self) -> Camera:
        return self._camera

    @property
    def entities(self) -> EntityManager:
        return self._entities

    @property
    def enemies(self) -> EntityManager:
        return self._enemies

    @property
    def player(self) -> Player:
        return self._player
