import pygame

from typing import TYPE_CHECKING

from scripts.entity import Entity, EntityManager

if TYPE_CHECKING:
    from scripts.game import Game
    from scripts.sprite import SpriteGroup


class Projectyle(Entity):
    def __init__(
        self,
        game: "Game",
        pos: pygame.Vector2,
        image: pygame.Surface,
        speed: float,
        damage: int,
        direction: pygame.Vector2,
        targets: Entity | EntityManager,
        *groups: "SpriteGroup",
        visible: bool = True
    ) -> None:
        """
        Representa um projétil qualquer

        Parameters
        ----------
        game : Game
            Jogo de origem
        pos : pygame.Vector2
            Posição inicial
        image : pygame.Surface
            Imagem associada ao sprite do projétil
        speed : float
            Velocidade de deslocamento
        damage : int
            Quanto dano o projétil dá
        direction : pygame.Vector2
            Direção de viagem
        targets : Entity | EntityManager
            Grupo contendo entidades que podem ser danificadas pelo projétil
        visible : bool, optional
            Se o projétil deve ser desenhado na tela, by default True
        """
        super().__init__(game, pos, image, *groups, visible=visible)

        # --- Movimento --- #
        self._direction: pygame.Vector2 = direction
        self._speed: float = speed

        # --- Dano --- #
        self._damage = damage
        self._targets = targets

    def update(self, dt: float) -> None:
        if self._move(self._speed * dt, self._direction) == True:
            self._health = -1

    def _check_hit(self) -> bool:
        """
        Verifica se interagiu com alguma entidade.

        Returns
        -------
        bool
            Se houve interação.
        """
        entities = self._targets
        hit: bool = False

        # --- Checa Hit --- #
        if isinstance(entities, EntityManager):
            assert isinstance(entities, EntityManager)
            for entity in entities:
                if self._hitbox.colliderect(entity.hitbox):
                    self._deal_damage(
                        entity,
                    )
                    hit = True
        else:
            assert isinstance(entities, Entity)
            if self._hitbox.colliderect(entities.hitbox):
                self._deal_damage(
                    entities,
                )
                hit = True

        return hit

    def _deal_damage(self, entity: Entity) -> None:
        """
        Dá dano em uma determinada entidade.

        Parameters
        ----------
        entity : Entity
            Entidade a ser danificada
        """
        entity.take_damage(self._damage, self._direction)
