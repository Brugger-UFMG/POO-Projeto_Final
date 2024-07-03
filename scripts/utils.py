import pygame

import os


def create_outline_text(
    text: str,
    text_color: pygame.Color,
    font_size: int,
    x: int,
    y: int,
    outline_size: int,
    outline_color: pygame.Color,
    colorkey: pygame.Color = pygame.Color(0, 0, 0),
) -> tuple[pygame.Surface, pygame.Rect]:
    font = pygame.font.Font(None, font_size)
    font.set_bold(True)

    outline_surf = font.render(text, True, outline_color)
    outline_surf.set_colorkey(colorkey)
    outline_surfsize = outline_surf.get_size()

    text_surf = pygame.Surface(
        (outline_surfsize[0] + 2 * outline_size, outline_surfsize[1] + 2 * outline_size)
    )
    text_surf.set_colorkey(colorkey)
    text_rect = text_surf.get_rect()

    offsets = [
        (ox, oy)
        for ox in range(-outline_size, 2 * outline_size, outline_size)
        for oy in range(-outline_size, 2 * outline_size, outline_size)
        if ox != 0 or oy != 0
    ]

    for ox, oy in offsets:
        px, py = text_rect.center
        text_surf.blit(outline_surf, outline_surf.get_rect(center=(px + ox, py + oy)))

    font.set_bold(False)
    inner_text = font.render(text, True, text_color).convert_alpha()
    text_surf.blit(inner_text, inner_text.get_rect(center=text_rect.center))

    text_rect.center = (x, y)
    return (text_surf, text_rect)


def load_image(path: str) -> pygame.Surface:
    """
    Carrega uma imagem

    Parameters
    ----------
    path : str
        Caminho para a imagem

    Returns
    -------
    pygame.Surface
    """
    if path.endswith(".png"):
        image = pygame.image.load(path).convert_alpha()
    else:
        image = pygame.Surface((0, 0))
    return image


def load_images(path: str) -> list[pygame.Surface]:
    """
    Carrega todas imagens de um diretório.

    Parameters
    ----------
    path : str
        Diretório contendo as imagens

    Returns
    -------
    list[pygame.Surface]
        Lista com todas imagens carregadas
    """
    images: list = []

    for image_name in os.listdir(path):
        images.append(load_image(path + image_name))

    return images


def load_directory(path: str) -> dict:
    """
    Carrega todas imagens de um diretório e seus sub-diretórios.

    Parameters
    ----------
    path : str
        Diretório a ser carregado.

    Returns
    -------
    dict
        Tudo o que foi carregado.
        Cada subdiretório recebe uma chave com seu nome,
        Caso hajam arquivos no proprio diretório, eles são salvos na chave "None".
    """
    directory: dict = {}
    has_files: bool = False

    # Verifica se o diretório tem arquivos e carrega seus subdiretórios
    for item in os.listdir(path):
        full_path = os.path.join(path, item)

        if os.path.isfile(full_path):
            has_files = True
        elif os.path.isdir(full_path):
            directory[item] = __load_directory_recursive(full_path + "/")

    # Carrega o diretório
    if has_files is True:
        directory["None"] = load_images(path)
    return directory


def __load_directory_recursive(path: str) -> dict | list:
    """
    Carrega todas imagens de um diretório e seus sub-diretórios.

    Parameters
    ----------
    path : str
        Diretório a ser carregado.

    Returns
    -------
    dict | list
        Tudo o que foi carregado.
        Os subdiretórios são carregados de forma recursiva, da seguinte forma:

        * Quando o diretório possui subdiretórios, uma chave será criada para
        cada subdiretório no dicionario com seu respectivo nome. Seu valor
        será ou um novo dicionário ou uma lista contendo as imagens

        * Quando o diretório não possui subdiretórios, será retornado apenas
        uma lista com as imagens.

        * Quando o diretório possui subdiretórios e imagens, a chave para as
        imagens no próprio diretório será "None", indicando que o subdiretório
        é ele mesmo.
    """
    directory: dict = {}

    has_files: bool = False
    has_folders: bool = False

    # Verifica se o diretório tem arquivos e carrega seus subdiretórios
    for item in os.listdir(path):
        full_path = os.path.join(path, item)

        if os.path.isfile(full_path):
            has_files = True
        elif os.path.isdir(full_path):
            has_folders = True
            directory[item] = __load_directory_recursive(full_path + "/")

    # Carrega o diretório
    if has_files is True:
        if has_folders is False:
            return load_images(path)
        else:
            directory["None"] = load_images(path)
    return directory


def is_within_bounds(x: int, y: int, width: int, height: int) -> bool:
    """
    Verifica se uma corrdenada x e y está dentro dos limites de largura e altura impostos.

    Parameters
    ----------
    x : int
    y : int
    width : int
        Largura da área
    height : int
        Altra da área

    Returns
    -------
    bool
    """
    return 0 <= x < width and 0 <= y < height
