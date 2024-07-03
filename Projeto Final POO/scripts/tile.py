import pygame

from typing import TYPE_CHECKING

from scripts.sprite import Sprite, SpriteGroup

if TYPE_CHECKING:
    from scripts.map import Map


class Tile(Sprite):
    def __init__(
        self,
        map: "Map",
        pos: pygame.Vector2,
        image: pygame.Surface,
        collider_inflate: tuple[int, int],
        collider_move: tuple[int, int],
        *groups: SpriteGroup,
        visible: bool = True,
        collidable: bool = False
    ) -> None:
        """
        Representa uma tile no mapa.

        Parameters
        ----------
        map : Map
            Mapa de origem.
        pos : pygame.Vector2
            Posição em pixels.
        image : pygame.Surface
            Imagem associada.
        collider_inflate : tuple[int, int]
            O quanto inflar o colisor.
        collider_move : tuple[int, int]
            O quanto deslocar o colisor.
        visible : bool, optional
            Se a tile é visível, by default True
        collidable : bool, optional
            Se a tile pode colidir, by default False
        """
        # --- Setup Sprite --- #
        self._map: "Map" = map
        super().__init__(pos, image, *groups, visible=visible)

        # --- Colisão --- #
        self._collidable: bool = collidable
        collider: pygame.Rect = self._image.get_rect(topleft=pos)
        collider = collider.inflate(collider_inflate)
        collider = collider.move(collider_move)
        self._collider: pygame.Rect = collider

    @property
    def pos(self) -> pygame.Vector2:
        return self._pos

    @pos.setter
    def pos(self, pos: pygame.Vector2) -> None:
        self._pos = pos
        self._collider.topleft = (int(pos.x), int(pos.y))

    @property
    def tile_pos(self) -> tuple[int, int]:
        tile_size = self._map.tile_size
        return (int(self._pos.x // tile_size), int(self._pos.y // tile_size))

    @tile_pos.setter
    def tile_pos(self, pos: tuple[int, int]) -> None:
        tile_size = self._map.tile_size
        self.pos = pygame.Vector2((pos[0] * tile_size, pos[1] * tile_size))

    @property
    def collidable(self) -> bool:
        return self._collidable

    @property
    def collider(self) -> pygame.Rect:
        return self._collider
