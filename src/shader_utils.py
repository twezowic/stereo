# zmodyfikowany kod z WMM lab 8
import os
from dataclasses import dataclass
from typing import Dict


@dataclass
class ShaderCollection:
    fragment_shader: str = None
    vertex_shader: str = None
    geometry_shader: str = None

    def assign_shader(self, extension, shader_text):
        if extension in ['.frag','.fs']:
            self.fragment_shader = shader_text

        if extension in ['.vert','.vs']:
            self.vertex_shader = shader_text

    def is_valid_collection(self):
        return self.vertex_shader and self.fragment_shader

    def is_empty_collection(self):
        return not (self.vertex_shader or self.fragment_shader)


def _gather_shader_files(shader_directory_path: str) -> dict:
    file_names = os.listdir(shader_directory_path)

    shaders = {}

    for file_name in file_names:
        basename = os.path.splitext(file_name)[0]
        shaders.setdefault(basename, [])
        shaders[basename].append(os.path.join(shader_directory_path, file_name))

    return shaders


def _load_shader(shader_path: str) -> str:
    with open(shader_path) as f:
        shader_text = f.read()

    return shader_text


def get_shaders(shader_directory_path: str) -> Dict[str, ShaderCollection]:
    shaders = {}
    gathered_files = _gather_shader_files(shader_directory_path)

    for identifier, shader_path_list in gathered_files.items():
        shader_collection = ShaderCollection()

        for shader_path in shader_path_list:
            extension = os.path.splitext(shader_path)[1]
            shader_text = _load_shader(shader_path)
            shader_collection.assign_shader(extension, shader_text)

        if shader_collection.is_empty_collection():
            continue

        if not shader_collection.is_valid_collection():
            raise RuntimeError('Missing vertex or fragment shader')

        shaders[identifier] = shader_collection

    return shaders
