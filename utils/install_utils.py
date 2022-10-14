import os
import pathlib
import platform
import shutil
import zipfile

from core.constants import TEXTURES_PATH, RESOURCES_PATH


def install_textures():
    if os.path.isdir(TEXTURES_PATH):
        return

    if platform.system() != 'Windows':
        raise TextureInstallationError("Texture installer only supports Windows for now.")

    minecraft_install_path = os.path.join(os.environ['appdata'], '.minecraft', 'versions')
    if not os.path.isdir(minecraft_install_path):
        raise TextureInstallationError(
            f"Couldn't find Minecraft installed in the default directory: `{minecraft_install_path}`."
        )

    for version_path in sorted(pathlib.Path(minecraft_install_path).iterdir(), key=os.path.getctime, reverse=True):
        jar_path = os.path.join(version_path, f'{version_path.name}.jar')
        if os.path.isfile(jar_path):
            break

    else:
        raise TextureInstallationError(
            f"No version contains the .jar executable in the default installation directory: `{minecraft_install_path}`."
        )

    textures_jar_subdir = 'assets/minecraft/textures'
    with zipfile.ZipFile(jar_path) as jar:
        for file_path in jar.namelist():
            if file_path.startswith(textures_jar_subdir):
                jar.extract(file_path, RESOURCES_PATH)

    shutil.move(os.path.join(RESOURCES_PATH, textures_jar_subdir), RESOURCES_PATH)
    shutil.rmtree(os.path.join(RESOURCES_PATH, textures_jar_subdir.split('/', 1)[0]))


class TextureInstallationError(Exception):
    pass
