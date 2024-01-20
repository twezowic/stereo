import moderngl_window
import moderngl
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
        self.init_shaders_variables()
        self.scene = self.load_scene('complex.obj')
        self.lights = scene_settings.get_lights()
        self.instance = self.scene.root_nodes[0].mesh.vao.instance(self.program)

    def get_program(self):
        shaders = shader_utils.get_shaders(os.path.dirname(os.path.realpath(__file__))+'/../resources/shader/')
        program = self.ctx.program(fragment_shader=shaders['phong'].fragment_shader, vertex_shader=shaders['phong'].vertex_shader)
        return program

    def init_shaders_variables(self):

        self.camera_pos = self.program["camera_position"]

        # make point lights form config
        lights_nparrays = scene_settings.get_lights()
        self.program["light_count"].value=len(lights_nparrays)
        for idx,point_light in enumerate(lights_nparrays):
            self.program[f"point_lights[{idx}].pos"].write(point_light.pos)
            self.program[f"point_lights[{idx}].color"].write(point_light.color)

        # ambient lighting settings
        colors = [x.color for x in lights_nparrays]
        self.program["ambient_color"].value=np.average(colors,axis=0)
        self.program["ambient_intensity"].value=len(lights_nparrays)*0.05