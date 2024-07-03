import pygame

from typing import TYPE_CHECKING
from weakref import ref

from scripts.sprite import SpriteGroup

if TYPE_CHECKING:
    from scripts.sprite import Sprite
    from scripts.map import Map
    from scripts.player import Player


class Camera:
    def __init__(
        self, display_surf: pygame.Surface, map: "Map", player: "Player"
    ) -> None:
        """
        Classe com metodos de draw customizados para renderizar o jogo
        com uma camera centrada no jogador.
        """
        # --- REFERENCIAS CONSTANTES de Controle --- #
        self._DISPLAY_SURF: pygame.Surface = display_surf
        self._MAP: "Map" = map
        self._PLAYER: "Player" = player

    def get_offset(self) -> pygame.Vector2:
        """
        Calcula o offset.

        Returns
        -------
        pygame.math.Vector2
            Offset em pixels
        """
        # --- Obtem o offset --- #
        offset = pygame.Vector2()

        offset.x = self._get_offset_1D(
            self._PLAYER.hitbox.centerx,
            int(self._DISPLAY_SURF.get_width() / 2),
            self._MAP.size_pixels[0],
        )
        offset.y = self._get_offset_1D(
            self._PLAYER.hitbox.centery,
            int(self._DISPLAY_SURF.get_height() / 2),
            self._MAP.size_pixels[1],
        )
        return offset

    def _get_offset_1D(
        self, player_center: int, display_center: int, map_size: int
    ) -> int:
        """
        Calcula uma única dimensão do offset.

        Parameters
        ----------
        player_center : int
            Centro do player em pixels
        camera_center : int
            Centro do display em pixels
        map_size : int
            Tamanho do mapa em pixels

        Returns
        -------
        int
            Offset em pixels
        """
        offset: int = 0
        map_center = map_size // 2
        display_size = display_center * 2

        if display_size >= map_size:
            offset = map_center - display_center
        else:
            if display_center > player_center:
                offset = 0
            elif player_center > map_size - display_center:
                offset = map_size - display_size
            else:
                offset = player_center - display_center

        return offset

    def render_sprites(self, sprite_group: SpriteGroup["Sprite"]) -> None:
        """
        Desenha sprites no display como vistos pela camera.

        Parameters
        ----------
        sprites : list[pygame.sprite.Group]
            Grupo contendo os sprites a serem desenhados
        """
        # --- Obtem o offset --- #
        offset = self.get_offset()

        # --- Desenhando os Sprites --- #
        for sprite in sprite_group:
            sprite.draw(self._DISPLAY_SURF, -offset)

    def render_sprites_y_sorted(self, sprite_group: SpriteGroup["Sprite"]) -> None:
        """
        Desenha sprites no display como vistos pela camera,
        ordenados de acordo com suas posições y no mapa.

        Parameters
        ----------
        sprites : list[pygame.sprite.Group]
            Grupo contendo os sprites a serem desenhados
        """
        # --- Obtem o offset --- #
        offset = self.get_offset()

        # --- Desenhando os Sprites --- #
        for sprite in sorted(sprite_group.items(), key=lambda sprite: sprite.pos.y):
            sprite.draw(self._DISPLAY_SURF, -offset)

    def get_original_pos(self, pos: pygame.Vector2) -> pygame.Vector2:
        """
        A partir de uma posição deslocada pela câmera, retorna
        sua posição equivalente sem o offset.

        Parameters
        ----------
        pos : tuple[int, int]
            Posição com offset

        Returns
        -------
        tuple[int, int]
            Posição original
        """
        # --- Obtem o offset --- #
        offset = self.get_offset()

        return pos + offset
