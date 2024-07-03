import pygame

from copy import deepcopy
from typing import TYPE_CHECKING

from scripts.entity import Entity
from scripts.projectyle import Projectyle
from scripts.sprite import MovingSprite

if TYPE_CHECKING:
    from scripts.game import Game
    from scripts.sprite import SpriteGroup


class Player(Entity):
    def __init__(
        self,
        game: "Game",
        pos: pygame.Vector2,
        image: pygame.Surface,
        *groups: "SpriteGroup",
        visible: bool = True
    ) -> None:
        """
        Representa o Jogador.

        Parameters
        ----------
        game : Game
            Jogo de origem
        pos : pygame.Vector2
            Posição inicial
        image : pygame.Surface
            Imagem associada ao sprite
        visible : bool, optional
            Se o jogador é visível, by default True
        """
        # --- Setup Entity --- #
        super().__init__(game, pos, image, *groups, visible=visible)
        self._mouse_pos: pygame.Vector2 = pygame.Vector2()

        # --- Vida --- #
        self._max_health: int = 6  # deve ser multiplo de 2
        self._health: int = self._max_health
        self._vulnerable: bool = True
        self._grace_time: float = 1
        self._invulnerable_time: float = 0

        # --- Movimento --- #
        self._speed: float = 100
        self._knockback_resistance: int = 70
        self._knockback: float = 0.0
        self._knockback_travelled: float = 0.0
        self._knockback_direction: pygame.Vector2 = pygame.Vector2()

        # --- Ataque --- #
        self._damage: int = 1
        self._attacking: bool = False
        self._can_attack: bool = False
        self._attack_cooldown: float = 0.25
        self._attack_time: float = 0.0
        self._shot_speed: float = 500.0

        # --- Esquiva --- #
        self._dodging: bool = False
        self._dodge_released: bool = True
        self._dodge_cooldown: float = 1.2
        self._air_time: float = 0.4
        self._dodge_time: float = 0.0
        self._dodge_speed: float = 200
        self._dodge_direction: pygame.Vector2 = pygame.Vector2((0, 1))

    def update(self, dt: float) -> None:
        if self.check_death() == False:
            if self._dodging and self._dodge_time >= (
                self._dodge_cooldown - self._air_time
            ):
                self._dodge(dt)
            else:
                self.__input()
                self._move(self._speed * dt, self._direction)

            self._cooldowns(dt)
            self._take_knockback(dt)
            self.blink()
        else:
            self._cooldowns(dt)
            self._vulnerable = False
            self._take_knockback(dt)

    def __input(self) -> None:
        """
        Gerencia o input para o jogador.
        """
        keys = pygame.key.get_pressed()
        self._mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

        mouse_buttons = pygame.mouse.get_pressed()

        # --- Movimento --- #
        # Vertical
        if keys[pygame.K_w]:
            if keys[pygame.K_s]:
                self._direction.y = 0
            else:
                self._direction.y = -1
        elif keys[pygame.K_s]:
            self._direction.y = 1
        else:
            self._direction.y = 0

        # Horizontal
        if keys[pygame.K_a]:
            if keys[pygame.K_d]:
                self._direction.x = 0
            else:
                self._direction.x = -1
        elif keys[pygame.K_d]:
            self._direction.x = 1
        else:
            self._direction.x = 0

        # --- Ataque --- #
        if mouse_buttons[0] is True and not self._attacking and self._can_attack:
            self._attacking = True
            self._can_attack = False
            self._attack_time = self._attack_cooldown
            self._attack(self._get_entity_distance_direction(self._mouse_pos)[1])

        # --- Esquiva --- #
        if keys[pygame.K_SPACE]:
            if not self._dodging and self._dodge_released:
                self._dodge_released = False
                self._dodging = True
                self._dodge_time = self._dodge_cooldown
                self._dodge_travelled = 0.0
                self._can_attack = False
                self._attack_time = self._attack_cooldown + self._dodge_cooldown / 2
                self._vulnerable = False
                self._invulnerable_time = self._air_time
        else:
            self._dodge_released = True

        if self._direction.magnitude() > 0:
            self._direction.normalize()
            self._dodge_direction = deepcopy(self._direction)

    def _attack(self, direction: pygame.Vector2) -> None:
        """
        Realiza um ataque.

        Parameters
        ----------
        direction : pygame.Vector2
            Direção do ataque
        """
        self._game.entities.add(
            Projectyle(
                self._game,
                deepcopy(self._pos),
                self._game.graphics["entities"]["projectiles"]["player_bullet"][0],
                self._shot_speed,
                self._damage,
                -self._get_entity_distance_direction(
                    self._game.camera.get_original_pos(
                        self._mouse_pos
                        / (
                            self._game.window.get_width()
                            / self._game.display.get_width()
                        )
                    ),
                )[1],
                self._game.enemies,
            )
        )

    def _dodge(self, dt: float) -> None:
        """
        Se movimenta em esquiva.

        Parameters
        ----------
        dt : float
            Tempo desde a última chamada desse método
        """
        self._move(self._dodge_speed * dt, self._dodge_direction)

    def _cooldowns(self, dt: float) -> None:
        super()._cooldowns(dt)

        if self._dodging:
            self._dodge_time -= dt
            if self._dodge_time <= 0:
                self._dodging = False
                self._dodge_time = 0.0

    @property
    def max_health(self) -> int:
        return self._max_health

    @property
    def health(self) -> int:
        return self._health

    @health.setter
    def health(self, health) -> None:
        if health > self._max_health:
            self._health = self._max_health
        else:
            self._health = health

    @property
    def shot_speed(self) -> float:
        return self._shot_speed

    @property
    def image(self) -> pygame.Surface:
        return self._image

    @image.setter
    def image(self, image: pygame.Surface) -> None:
        self._image = image
