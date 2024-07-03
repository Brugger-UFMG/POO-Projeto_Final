import pygame

from copy import deepcopy
from typing import TYPE_CHECKING

from scripts.entity import Entity, EntityManager
from scripts.projectyle import Projectyle

if TYPE_CHECKING:
    from scripts.game import Game
    from scripts.sprite import SpriteGroup


class Enemy(Entity):
    # Quantos pontos vale matar o inimigo
    _value: int = 0

    def __init__(
        self,
        game: "Game",
        pos: pygame.Vector2,
        image: pygame.Surface,
        *groups: "SpriteGroup",
        visible: bool = True
    ) -> None:
        """
        Classe que representa um inimigo genêrico.

        Parameters
        ----------
        game : Game
            Jogo ao qual o inimigo pertence
        pos : pygame.Vector2
            Posição inicial
        image : pygame.Surface
            Imagem associada
        visible : bool, optional
            Se o inimigo deve ser desenhado na tela, by default True
        """
        # --- Setup Simulated Entity --- #
        super().__init__(game, pos, image, *groups, visible=visible)

        # --- IA --- #
        self._detection_range: float = 200.0
        self._attack_range: float = 160.0
        self._state: str = "idle"
        self._player_dist_dir: tuple[float, pygame.Vector2]
        self._projectyles: EntityManager = EntityManager()
        self._grace_time: float = 0.8

    def _check_state(self) -> None:
        """
        Calcula o estado atual da IA do inimigo.
        """
        self._player_dist_dir = self._get_entity_distance_direction(
            self._game.player.pos
        )

        if self._player_dist_dir[0] <= self._attack_range:
            self._state = "attacking"
        elif self._player_dist_dir[0] <= self._detection_range:
            self._state = "seeking"
        else:
            self._state = "idle"

    def _attack(self) -> bool:
        """
        Tenta realizar um ataque de acordo com o estado interno do inimigo.

        Returns
        -------
        bool
            Se o ataque foi realizado
        """
        if self._can_attack == True:
            self._attacking = True
            self._can_attack = False
            self._attack_time = self._attack_cooldown
            return True
        return False

    @property
    def projectyles(self) -> EntityManager:
        return self._projectyles

    @property
    def value(self) -> int:
        return self.__class__._value


class Hornet(Enemy):
    _value: int = 10

    def __init__(
        self,
        game: "Game",
        pos: pygame.Vector2,
        *groups: "SpriteGroup",
        visible: bool = True
    ) -> None:
        """
        Representa uma Hornet (Inimigo).

        Parameters
        ----------
        game : Game
            Jogo de origem
        pos : pygame.Vector2
            Posição inicial
        visible : bool, optional
            Se deve ser desenhado, by default True
        """
        # --- Setup Enemy --- #
        image = game.graphics["entities"]["enemies"]["hornet"][0]
        super().__init__(game, pos, image, *groups, visible=visible)

        # --- Vida --- #
        self._max_health: int = 1
        self._health: int = self._max_health

        # --- Movimento --- #
        self._stop_range: float = 50.0
        self._speed: float = 80.0
        self._knockback_resistance: int = 200

        # --- Ataque --- #
        self._attack_cooldown: float = 0.75
        self._shot_speed: float = 100.0
        self._damage: int = 1

    def update(self, dt: float) -> None:
        if self.check_death() == False:
            self._check_state()
            if self._state == "seeking":
                self._move(self._speed * dt, -self._player_dist_dir[1])
            if self._state == "attacking":
                if self._player_dist_dir[0] >= self._stop_range:
                    self._move(self._speed / 2 * dt, -self._player_dist_dir[1])
                self._attack()

            self._cooldowns(dt)
            self._take_knockback(dt)
            self.blink()

    def _attack(self) -> bool:
        if super()._attack() == True:
            self._projectyles.add(
                Projectyle(
                    self._game,
                    deepcopy(self._pos),
                    self._game.graphics["entities"]["projectiles"]["enemy_bullet"][0],
                    self._shot_speed,
                    self._damage,
                    -self._player_dist_dir[1],
                    self._game.player,
                )
            )
            return True
        return False


class Spider(Enemy):
    _value: int = 20

    def __init__(
        self,
        game: "Game",
        pos: pygame.Vector2,
        *groups: "SpriteGroup",
        visible: bool = True
    ) -> None:
        """
        Representa uma Spider (Inimigo).

        Parameters
        ----------
        game : Game
            Jogo de origem
        pos : pygame.Vector2
            Posição inicial
        visible : bool, optional
            Se deve ser desenhado, by default True
        """
        # --- Setup Enemy --- #
        image = game.graphics["entities"]["enemies"]["spider"][0]
        super().__init__(game, pos, image, *groups, visible=visible)

        # --- Vida --- #
        self._max_health: int = 2
        self._health: int = self._max_health

        # --- Movimento --- #
        self._detection_range: float = 300.0
        self._attack_range: float = 180.0
        self._stop_range: float = 100.0
        self._speed: float = 150.0
        self._knockback_resistance: int = 200

        # --- Ataque --- #
        self._attack_cooldown: float = 1
        self._shot_speed: float = 100.0
        self._damage: int = 1

    def update(self, dt: float) -> None:
        if self.check_death() == False:
            self._check_state()
            if self._state == "seeking":
                self._move(self._speed * dt, -self._player_dist_dir[1])
            if self._state == "attacking":
                if self._player_dist_dir[0] >= self._stop_range:
                    self._move(self._speed / 2 * dt, -self._player_dist_dir[1])
                self._attack()

            self._cooldowns(dt)
            self._take_knockback(dt)
            self.blink()

    def _attack(self) -> bool:
        if super()._attack() == True:
            rotate_ammount = 360 / 8
            angle = pygame.Vector2(0, 1)
            for i in range(8):
                angle = angle.rotate(rotate_ammount)

                self._projectyles.add(
                    Projectyle(
                        self._game,
                        deepcopy(self._pos),
                        self._game.graphics["entities"]["projectiles"]["enemy_bullet"][
                            0
                        ],
                        self._shot_speed,
                        self._damage,
                        angle,
                        self._game.player,
                    )
                )
            return True
        return False


class Beetle(Enemy):
    _value: int = 40

    def __init__(
        self,
        game: "Game",
        pos: pygame.Vector2,
        *groups: "SpriteGroup",
        visible: bool = True
    ) -> None:
        """
        Representa um Beetle (Inimigo).

        Parameters
        ----------
        game : Game
            Jogo de origem
        pos : pygame.Vector2
            Posição inicial.
        visible : bool, optional
            Se deve ser desenhado, by default True
        """
        # --- Setup Enemy --- #
        image = game.graphics["entities"]["enemies"]["beetle"][0]
        super().__init__(game, pos, image, *groups, visible=visible)

        # --- Vida --- #
        self._max_health: int = 3
        self._health: int = self._max_health

        # --- Movimento --- #
        self._detection_range: float = 400.0
        self._attack_range: float = 150.0
        self._speed: float = 40.0
        self._knockback_resistance: int = 100

        # --- Ataque --- #
        self._attack_cooldown: float = 3
        self._shot_speed: float = 100.0
        self._damage: int = 1

        self._attack_cycle: int = 3
        self._attack_option: int = 0
        self._attack_cycle_cooldown: float = 0.2
        self._attack_cycle_time: float = 0.0

        self._deffending: bool = False
        self._deffending_time: float = 0.5

    def update(self, dt: float) -> None:
        if self.check_death() == False:
            self._check_state()
            if self._state == "seeking":
                self._move(self._speed * dt, -self._player_dist_dir[1])
            if self._state == "attacking":
                self._attack()
            if self._state == "deffending":
                self._vulnerable = False
                self._invulnerable_time = self._attack_time + self._deffending_time
                self._deffending = True
            else:
                self._deffending = False

            self._cooldowns(dt)
            self._take_knockback(dt)
            self.blink()

    def _check_state(self) -> None:
        super()._check_state()
        if self._attack_time > self._deffending_time and self._attack_time < (
            self._attack_cooldown - self._deffending_time
        ):
            self._state = "deffending"

    def _attack(self) -> bool:
        if self._attack_option < self._attack_cycle and self._attack_cycle_time == 0:

            self._attack_option += 1
            self._attack_cycle_time = self._attack_cycle_cooldown

            rotate_ammount = 360 / ((self._attack_option + 1) ** 2)
            angle = pygame.Vector2(0, 1)
            for i in range(((self._attack_option + 1) ** 2)):
                angle = angle.rotate(rotate_ammount)

                self._projectyles.add(
                    Projectyle(
                        self._game,
                        deepcopy(self._pos),
                        self._game.graphics["entities"]["projectiles"]["enemy_bullet"][
                            0
                        ],
                        self._shot_speed,
                        self._damage,
                        angle,
                        self._game.player,
                    )
                )

        if self._can_attack == True:
            self._attacking = True
            if self._attack_option >= self._attack_cycle:
                self._can_attack = False
                self._attack_time = self._attack_cooldown
            return True
        return False

    def _cooldowns(self, dt: float) -> None:
        if not self._vulnerable and not self._deffending:
            self._invulnerable_time -= dt
            if self._invulnerable_time <= 0:
                self._vulnerable = True
                self._invulnerable_time = 0.0

        if not self._can_attack or self._attacking:
            self._attack_time -= dt
            if self._attack_time <= 0:
                self._can_attack = True
                self._attacking = False
                if self._attack_option >= self._attack_cycle:
                    self._attack_option = 0

        if self._knockback > 0:
            self._knockback -= self._knockback_resistance * dt
        else:
            self._knockback = 0.0

        if self._attack_cycle_time > 0:
            self._attack_cycle_time -= dt
        else:
            self._attack_cycle_time = 0.0

    def take_damage(self, ammount: int, direction: pygame.Vector2) -> None:
        super().take_damage(ammount, direction)

        if self._deffending == True:
            self._projectyles.add(
                Projectyle(
                    self._game,
                    deepcopy(self._pos),
                    self._game.graphics["entities"]["projectiles"]["enemy_bullet"][0],
                    self._game.player.shot_speed / 2,
                    self._damage,
                    -direction,
                    self._game.player,
                )
            )
