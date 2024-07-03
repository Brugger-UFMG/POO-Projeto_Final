import pygame

from collections import deque
import sys

from scripts.game import Game


class Main:
    # --- CONSTANTES de Controle --- #
    # Tamanho da superficie onde o jogo sera desenhado
    # - Por ser um jogo em pixel art ele deve ser renderizado em baixa resolução
    __game_width: int = 640
    __game_height: int = 360

    # Tamanho da janela do jogo
    # - A pixel art sera redimensionada para essa janela maior
    __scale_factor: int = 2  # Use numeros inteiros para manter a pixel art bonita
    __width: int = __game_width * __scale_factor
    __height: int = __game_height * __scale_factor

    __max_FPS = 60

    def __init__(self) -> None:
        """
        Responsável por gerenciar o programa.
        """
        # --- Setup Pygame --- #
        pygame.init()

        # Janela principal do jogo
        self.__window: pygame.Surface = pygame.display.set_mode(
            (Main.__width, Main.__height),
            flags=pygame.SCALED | pygame.DOUBLEBUF,
        )
        pygame.display.set_caption("Projeto Final de POO")

        # Superficie onde o jogo sera desenhado
        self.__display: pygame.Surface = pygame.Surface(
            (Main.__game_width, Main.__game_height)
        )

        # Relogio do jogo / Limitador de FPS
        self.__clock: pygame.time.Clock = pygame.time.Clock()

        # --- VARIAVEIS de Controle --- #
        self.__running: bool = False
        self.__game: Game = Game(self.__window, self.__display)
        self.__dt: float = 1
        self.__FPS: deque = deque()

    def run(self) -> None:
        """
        Roda o programa.
        """
        self.__running = True

        # --- Loop Principal --- #
        while self.__running is True:
            self.__dt = self.__clock.tick(Main.__max_FPS) / 1000

            # --- Checa eventos do Pygame --- #
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # --- Atualiza Lógica e Display do Jogo --- #
            self.__game.run(self.__dt)

            font = pygame.font.Font(None, 30)
            text = font.render(
                f"FPS: {round(self.__get_average_FPS())}", True, "White", "Black"
            )
            self.__window.blit(text, (5, 5))

            pygame.display.update()

    def __get_average_FPS(self) -> float:
        """
        Calcula a média móvel dos valores de FPS.

        Returns
        -------
        float
            FPS médio
        """
        self.__FPS.append(1 / (self.__dt))
        if len(self.__FPS) > self.__max_FPS:
            self.__FPS.popleft()
        return sum(self.__FPS) / len(self.__FPS)


# Este codigo deve ser executado somente quando este arquivo for o Main
if __name__ == "__main__":
    process = Main()
    process.run()
