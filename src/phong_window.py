import moderngl_window
import moderngl
import pywavefront
from moderngl_window.context.base.window import BaseWindow
from moderngl_window.timers.base import BaseTimer
import os
import numpy as np

import scene_settings
import shader_utils


class PhongWindow(moderngl_window.WindowConfig):

    def __init__(self, ctx: moderngl.Context = None, wnd: BaseWindow = None, timer: BaseTimer = None, **kwargs):
        super().__init__(ctx, wnd, timer, **kwargs)
        self.program = self.get_program()
        self.init_shaders_variables(material_path='../resources/scena_full.obj', material_name='Material.001')
        self.scene = self.load_scene('scena_full.obj')
        self.pywavefront_scene = pywavefront.Wavefront('../resources/scena_full.obj', collect_faces=True)
        self.lights = scene_settings.get_lights()
        self.instance = self.scene.root_nodes[0].mesh.vao.instance(self.program)

    def get_program(self):
        shaders = shader_utils.get_shaders(os.path.dirname(os.path.realpath(__file__)) + '/../resources/shader/')
        program = self.ctx.program(fragment_shader=shaders['phong'].fragment_shader,
                                   vertex_shader=shaders['phong'].vertex_shader)
        return program

    def init_shaders_variables(self, material_path='../resources/scena_full.obj', material_name='Material.001'):
        self.camera_pos = self.program["camera_position"]

        # make point lights form config
        lights_nparrays = scene_settings.get_lights()
        self.program["light_count"].value = len(lights_nparrays)
        for idx, point_light in enumerate(lights_nparrays):
            self.program[f"point_lights[{idx}].pos"].write(point_light.pos)
            self.program[f"point_lights[{idx}].color"].write(point_light.color)

    def update_current_material(self, current_mesh):
        material_properties = self.get_material_properties(current_mesh)

        # set material properties in shader
        self.program["Ka"].value = material_properties["Ka"]
        self.program["Kd"].value = material_properties["Kd"]
        self.program["Ks"].value = material_properties["Ks"]
        self.program["Ns"].value = material_properties["Ns"]

    def get_material_properties(self, mesh):
        # Get the material properties for mesh in current scene

        
        material = self.pywavefront_scene.meshes[mesh.name].materials[0]  # Replace 'material_name' with the name of your material
        Ka = tuple(material.ambient)[:3]
        Kd = tuple(material.diffuse)[:3]
        Ks = tuple(material.specular)[:3]
        Ns = material.shininess
        return {'Ka': Ka, 'Kd': Kd, 'Ks': Ks, 'Ns': Ns}
