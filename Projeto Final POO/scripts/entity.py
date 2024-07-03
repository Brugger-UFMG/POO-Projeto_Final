import pygame

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from math import sin

from scripts.sprite import MovingSprite, SpriteGroup

if TYPE_CHECKING:
    from scripts.game import Game


class Simulated(ABC):
    @abstractmethod
    def update(self, dt: float) -> None:
        """
        Atualiza a lógica interna.

        Parameters
        ----------
        dt : float
            Tempo passado desde a última chamada desse método.
        """
        pass


class Entity(MovingSprite, Simulated):
    def __init__(
        self,
        game: "Game",
        pos: pygame.Vector2,
        image: pygame.Surface,
        *groups: SpriteGroup,
        visible: bool = True
    ) -> None:
        """
        Representa uma Entidade Abstrata.

        Parameters
        ----------
        game : Game
            Jogo de origem
        pos : pygame.Vector2
            Posição Inicial
        image : pygame.Surface
            Imagem associada ao sprite
        visible : bool, optional
            Se o sprite é visível, by default True
        """
        # --- Setup MovingSprite --- #
        super().__init__(game, pos, image, *groups, visible=visible)

        # --- Vida --- #
        self._max_health: int = 6
        self._health: int = self._max_health
        self._vulnerable: bool = True
        self._grace_time: float = 0.25
        self._invulnerable_time: float = 0

        # --- Movimento --- #
        self._knockback_resistance: int = 40
        self._knockback: float = 0.0
        self._knockback_direction = pygame.Vector2()

        # --- Ataque --- #
        self._attacking: bool = False
        self._can_attack: bool = False
        self._attack_cooldown: float = 0.5
        self._attack_time: float = 0.0
        self._shot_speed: float = 1.0
        self._damage: int = 1

    def _cooldowns(self, dt: float) -> None:
        """
        Atualiza os timers internos.

        Parameters
        ----------
        dt : float
            Tempo passado desde a última chamada desse método.
        """
        if not self._vulnerable:
            self._invulnerable_time -= dt
            if self._invulnerable_time <= 0:
                self._vulnerable = True
                self._invulnerable_time = 0.0

        if not self._can_attack or self._attacking:
            self._attack_time -= dt
            if self._attack_time <= 0:
                self._can_attack = True
                self._attacking = False

        if self._knockback > 0:
            self._knockback -= self._knockback_resistance * dt
        else:
            self._knockback = 0.0

    def check_death(self) -> bool:
        """
        Verifica se está morto.

        Returns
        -------
        bool
        """
        return self._health <= 0

    def take_damage(self, ammount: int, direction: pygame.Vector2) -> None:
        """
        Reduz a vida e aplica knockback a entidade.

        Parameters
        ----------
        ammount : int
            Quanto dano
        direction : pygame.Vector2
            Direção do knockback
        """
        if self._vulnerable == True:
            self._health -= ammount

            self._knockback = ammount * 100 / self._max_health
            self._knockback_direction = direction

            self._vulnerable = False
            self._invulnerable_time = self._grace_time

    def _take_knockback(self, dt: float) -> None:
        """
        Movimenta a entidade de acordo com o knockback.

        Parameters
        ----------
        dt : float
            Tempo desde a última chamada desse método.
        """
        self._move(self._knockback * 10 * dt, self._knockback_direction)

    def _get_entity_distance_direction(
        self, pos: pygame.Vector2
    ) -> tuple[float, pygame.Vector2]:
        """
        Calcula a distancia e direção da entidade para uma coordenada

        Parameters
        ----------
        pos: Pygame.Vector2

        Returns
        -------
        tuple[float, float]
            Tuple contendo direção (0) e angulo (1) obtidos
        """
        self_vector = self.pos
        entity_vector = pos
        distance = self_vector.distance_to(entity_vector)
        if distance > 0:
            direction = (self_vector - entity_vector).normalize()
        else:
            direction = pygame.Vector2((0, 0))
        return (distance, direction)

    def blink(self):
        """
        Pisca o sprite da entidade caso esteja invulnerável.
        """
        if self._vulnerable == False:
            opacity = sin(self._invulnerable_time * 50)
            # self._image.set_alpha(int(abs(opacity * 255)))
            if opacity < 0:
                self._visible = False
            else:
                self._visible = True
        else:
            # self._image.set_alpha(255)
            self._visible = True

    @property
    def vulnerable(self) -> bool:
        return self._vulnerable


class EntityManager(SpriteGroup[Entity]):
    def __init__(self, *entities: Entity) -> None:
        """
        Grupo para gerenciar diversas Entities.

        Parameters
        ----------
        *entities : Entity
            Entidades a serem adicionados ao grupo
        """
        super().__init__()
        self._internal_type = Entity
        self.add(*entities)

    def update(self, dt: float) -> None:
        """
        Chama o método de update de todas entidades no grupo.

        Parameters
        ----------
        dt : float
            Tempo desde a última chamada desse método
        """
        for entity in self._item_set:
            entity.update(dt)

    def check_deaths(self) -> list[Entity]:
        """
        Verifica entidades mortas dentro do grupo e as deleta.

        Returns
        -------
        list[Entity]
            Entidades deletadas
        """
        to_remove: list[Entity] = []
        for entity in self:
            if entity.check_death() == True:
                to_remove.append(entity)

        for entity in to_remove:
            entity.kill()

        return to_remove
