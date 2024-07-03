import pygame

from math import copysign
from weakref import WeakSet
from collections.abc import Iterator
from typing import Literal, Generic, TypeVar, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.game import Game
    from scripts.tile import Tile
    from scripts.entity import Entity


class Sprite:
    def __init__(
        self,
        pos: pygame.Vector2,
        image: pygame.Surface,
        *groups: "SpriteGroup",
        visible: bool = True,
    ) -> None:
        """
        Representa uma imagem na tela.

        Parameters
        ----------
        pos : pygame.Vector2
            Posição na tela (em pixels)
        image : pygame.Surface
            Surface contendo a imagem
        visible : bool, optional
            Se a imagem deve ser desenhada, by default True
        """
        # --- Imagem --- #
        self._pos = pos  # Se refere ao topo esquerdo do sprite
        self._image = image
        self._visible = visible

        # --- Grupos --- #
        self.__groups: WeakSet = WeakSet()
        if groups:
            self.add_to(*groups)

    def add_to(
        self,
        *groups: "SpriteGroup",
    ) -> None:
        """
        Adiciona o sprite a um grupo ou conjunto de grupos.

        Parameters
        ----------
        *groups : "SpriteGroup"
            Grupo ou conjunto de grupos

        Raises
        ------
        TypeError
            Todos grupos devem ser do tipo "SpriteGroup"
        """
        for group in groups:
            if not isinstance(group, SpriteGroup):
                raise TypeError(f"Elemento {group} não é do tipo SpriteGroup!")
            else:
                if not group in self.__groups:
                    self.__groups.add(group)
                    group.add(self)

    def remove_internal(self, *groups: "SpriteGroup") -> None:
        """
        Remove o sprite de um grupo sem notificar o grupo sobre a remoção.

        Parameters
        ----------
        *groups : "SpriteGroup"
            Grupo ou conjunto de grupos
        """
        for group in groups:
            if group in self.list_groups():
                self.__groups.remove(group)

    def remove_from(self, *groups: "SpriteGroup") -> None:
        """
        Remove o sprite de um grupo ou conjunto de grupos.

        Parameters
        ----------
        *groups : "SpriteGroup"
            Grupo ou conjunto de grupos
        """
        for group in groups:
            if group in self.list_groups():
                self.__groups.remove(group)
                group.remove(self)

    def list_groups(self) -> list["SpriteGroup"]:
        """
        Retorna uma lista iterável de todos os grupos que o sprite faz parte.

        Returns
        -------
        list[Sprite_Group]
        """
        return list(self.__groups)

    def draw(
        self,
        surface: pygame.Surface,
        offset: pygame.Vector2 = pygame.Vector2(),
    ) -> None:
        """
        Desenha o sprite em uma superficie, caso ele seja visível.

        Parameters
        ----------
        surface : pygame.Surface
            Superficie de destino.
        offset : pygame.Vector2, opcional
            Offset a partir da posição do sprite, by default 0
        """
        if self._visible:
            if offset == None:
                offset = pygame.Vector2((0, 0))
            position = (round(self._pos.x + offset.x), round(self._pos.y + offset.y))
            surface.blit(self._image, position)

    def kill(self) -> None:
        """
        Remove o sprite de todos grupos dos quais ele faz parte.
        """
        for group in self.__groups:
            group.remove_internal(self)
        self.__groups.clear()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} em {len(self.list_groups())} Grupo(s)"

    @property
    def pos(self) -> pygame.Vector2:
        return self._pos

    @property
    def visible(self) -> bool:
        return self._visible


class MovingSprite(Sprite):
    def __init__(
        self,
        game: "Game",
        pos: pygame.Vector2,
        image: pygame.Surface,
        *groups: "SpriteGroup",
        visible: bool = True,
    ) -> None:
        """
        Representa um Sprite que pode se movimentar e colidir

        Parameters
        ----------
        game : Game
            Jogo que originou o Sprite
        pos : pygame.Vector2
            Posição em pixels
        image : pygame.Surface
            Imagem associada ao Sprite
        visible : bool, optional
            Se o sprite deve ser desenhado, by default True
        """
        # --- Setup Sprite --- #
        self._game: "Game" = game
        super().__init__(pos, image, *groups, visible=visible)

        # --- Colisão --- #
        self._collider: pygame.Rect = self._image.get_rect(topleft=pos)
        self._hitbox: pygame.Rect = self.collider.inflate((-4, -4))

        # --- Movimento --- #
        self._direction: pygame.Vector2 = pygame.Vector2()
        self._speed: float = 0.0

    def _get_obstacles(self) -> set["Tile"]:
        """
        Obtem os obstaculos proximos.

        Returns
        -------
        set[Tile]
            Tiles encontradas
        """
        # --- Setup --- #
        obstacles: set["Tile"] = set()

        # --- Puxa os obstaculos do mapa --- #
        for tile in self._game.map.get_tiles_square(self.tile_pos):
            if tile.collidable == True:
                obstacles.add(tile)
        return obstacles

    def _get_entities(self) -> set["Entity"]:
        """
        Obtem as entidades que podem ser interagidas.

        Returns
        -------
        set[Entity]
            Entidades encontradas
        """
        # Este método deve ser implementado pelas classes herdeiras.
        return set()

    def _move(self, distance: float, direction: pygame.Vector2) -> bool:
        """
        Movimenta uma distância em uma dada direção.

        Parameters
        ----------
        distance : float
            Distância em pixels para movimentar
        direction : pygame.Vector2
            Vetor normalizado indicando a direção do movimento

        Returns
        -------
        bool
            Se houve colisão

        Raises
        ------
        ValueError
            O vetor direção não pode ser nulo
        """
        # --- Setup --- #
        collided: bool = False
        if direction.magnitude() > 0:
            direction = direction.normalize()

        distance_to_walk = pygame.Vector2(
            (abs(direction.x * distance), abs(direction.y * distance))
        )
        step = pygame.Vector2((self._hitbox.width, self._hitbox.height))

        # --- Movimento --- #
        while distance_to_walk.magnitude() != 0:
            # - Horizontal
            if distance_to_walk.x != 0:
                # Move um passo
                if distance_to_walk.x - (step.x * abs(direction.x)) < 0:
                    self._pos.x += copysign(distance_to_walk.x, direction.x)
                    distance_to_walk.x = 0
                else:
                    self._pos.x += step.x * direction.x
                    distance_to_walk.x -= step.x * abs(direction.x)
                self._collider.left = round(self._pos.x)
                self._hitbox.left = round(self._pos.x)
                # Verifica colisões
                if self.__colision("horizontal", direction) or self._check_hit():
                    collided = True
                    distance_to_walk.x = 0

            # - Vertical
            if distance_to_walk.y != 0:
                # Move um passo
                if distance_to_walk.y - (step.y * abs(direction.y)) < 0:
                    self._pos.y += copysign(distance_to_walk.y, direction.y)
                    distance_to_walk.y = 0
                else:
                    self._pos.y += step.y * direction.y
                    distance_to_walk.y -= step.y * abs(direction.y)
                self._collider.top = round(self._pos.y)
                self._hitbox.top = round(self._pos.y)
                # Verifica colisões
                if self.__colision("vertical", direction) or self._check_hit():
                    collided = True
                    distance_to_walk.y = 0
        # Acerta o movimento da hitbox
        return collided

    def __colision(
        self, direction: Literal["vertical", "horizontal"], move_dir: pygame.Vector2
    ) -> bool:
        """
        Verifica se houveram colisões.

        Parameters
        ----------
        direction : str, "horizontal" or "vertical"
            Tipo de colisão a ser verificada

        Returns
        -------
        bool
            Se houve colisão
        """
        collision: bool = False

        # --- Colisões na horizontal --- #
        if direction == "horizontal":

            for tile in self._get_obstacles():
                if self._collider.colliderect(tile.collider):
                    if move_dir.x > 0:  # Movendo para a Direita
                        self._collider.right = tile.collider.left
                        self._pos.x = self._collider.left
                        collision = True
                    elif move_dir.x < 0:  # Movendo para a Esquerda
                        self._collider.left = tile.collider.right
                        self._pos.x = self._collider.left
                        collision = True

        # --- Colisões na vertical --- #
        else:
            for tile in self._get_obstacles():
                if tile.collidable == True and self._collider.colliderect(
                    tile.collider
                ):
                    if move_dir.y > 0:  # Movendo para Baixo
                        self._collider.bottom = tile.collider.top
                        self._pos.y = self._collider.top
                        collision = True
                    elif move_dir.y < 0:  # Movendo para Cima
                        self._collider.top = tile.collider.bottom
                        self._pos.y = self._collider.top
                        collision = True

        # --- Conserta a posição --- #
        # self.pos = self._pos
        return collision

    def _check_hit(self) -> bool:
        """
        Verifica se interagiu com alguma entidade.

        Returns
        -------
        bool
            Se houve interação.
        """
        entities = self._get_entities()
        hit: bool = False

        # --- Checa Hit --- #
        for entity in entities:
            if entity.vulnerable and self._hitbox.colliderect(entity.hitbox):
                hit = True

        return hit

    @property
    def pos(self) -> pygame.Vector2:
        return self._pos

    @pos.setter
    def pos(self, pos: pygame.Vector2) -> None:
        self._pos = pos
        self._collider.topleft = (int(pos.x), int(pos.y))
        self._hitbox.topleft = (int(pos.x), int(pos.y))

    @property
    def tile_pos(self) -> tuple[int, int]:
        tile_size = self._game.map.tile_size
        return (int(self._pos.x // tile_size), int(self._pos.y // tile_size))

    @tile_pos.setter
    def tile_pos(self, pos: tuple[int, int]) -> None:
        tile_size = self._game.map.tile_size
        self.pos = pygame.Vector2((pos[0] * tile_size, pos[1] * tile_size))

    @property
    def hitbox(self) -> pygame.Rect:
        return self._hitbox

    @property
    def collider(self) -> pygame.Rect:
        return self._collider


Group_Type = TypeVar("Group_Type", bound=Sprite)


class SpriteGroup(Generic[Group_Type]):
    def __init__(self, *items: Group_Type) -> None:
        """
        Grupo para gerenciar diversos itens do tipo Sprite ou descendentes.

        Parameters
        ----------
        *items : (Group_Type)
            Itens a serem adicionados ao grupo
        """
        self._item_set: set[Group_Type] = set()
        self._internal_type: Type = Sprite
        self.add(*items)

    def items(self) -> list[Group_Type]:
        """
        Retorna uma lista com todos itens dentro do grupo.

        Returns
        -------
        list[Group_Type]
        """
        return list(self._item_set)

    def add(self, *items: Group_Type) -> None:
        """
        Adiciona um item ou coleção de itens ao grupo.

        Parameters
        ----------
        *items : (Group_Type)
            Itens a serem adicionados ao grupo

        Raises
        ------
        TypeError
            Todas entradas devem ser do tipo (Group_Type)
        """
        for item in items:
            if isinstance(item, self._internal_type):
                self._item_set.add(item)
                item.add_to(self)
            else:
                raise TypeError(
                    f"Elemento: {item} não é do tipo {self._internal_type}!"
                )

    def remove_internal(self, *items: Group_Type) -> None:
        """
        Remove o item do grupo sem notificar o item sobre a remoção.

        Parameters
        ----------
        *items : (Group_Type)
            Item ou conjunto de itens
        """
        for item in items:
            if self.has(item):
                self._item_set.remove(item)

    def remove(self, *items: Group_Type) -> None:
        """
        Remove um item ou coleção de itens do grupo.

        Parameters
        ----------
        *items : (Grop_Type)
            Itens a serem removidos do grupo
        """
        for item in items:
            if self.has(item):
                self._item_set.remove(item)
                item.remove_from(self)

    def empty(self) -> None:
        """
        Esvazia o grupo.
        """
        for item in self._item_set:
            item.remove_internal(self)
        self._item_set.clear()

    def has(self, *items: Group_Type) -> bool:
        """
        Verifica se o grupo possui ou nao um item ou coleção de itens.

        Returns
        -------
        bool
        """
        if not items:
            return False

        for item in items:
            if not item in self._item_set:
                return False
        return True

    def __iter__(self) -> Iterator[Group_Type]:
        return iter(self.items())

    def __contains__(self, item: Group_Type) -> bool:
        return self.has(item)

    def __len__(self) -> int:
        return len(self._item_set)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} contendo {len(self.items())} {self._internal_type}(s)"
