import moderngl_window
import moderngl
from moderngl_window.context.base.window import BaseWindow
from moderngl_window.timers.base import BaseTimer
import os
import numpy as np

import scene_settings
import shader_utils

anaglyph = True

class PhongWindow(moderngl_window.WindowConfig):

    def __init__(self, ctx: moderngl.Context = None, wnd: BaseWindow = None, timer: BaseTimer = None, **kwargs):
        super().__init__(ctx, wnd, timer, **kwargs)
        self.program = self.get_program()
        self.init_shaders_variables()
        self.scene = self.load_scene('suzanne.obj')
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

    

    def render(self, time, frametime):
        print(self.camera.position)
        print(self.camera.dir)
        self.camera.look_at([0.1,0.0,0.0])
        self.camera_pos.write(self.camera.position.astype('float32')) # how to lose 2 hours debugging
        self.program["projection"].write(self.camera.projection.matrix)
        self.program["view"].write(self.camera.matrix)

        self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
        self.ctx.clear(0.2, 0.2, 0.2, 0.0)
        #render red
        if anaglyph:
            self.ctx.fbo.depth_mask=False
            self.ctx.fbo.color_mask=(True,False,False,True)
            self.instance.render(moderngl.TRIANGLES)

            # move camera
            self.camera.position.x-=0.03
            self.camera_pos.write(self.camera.position.astype('float32')) # how to lose 2 hours debugging
            self.program["projection"].write(self.camera.projection.matrix)
            self.program["view"].write(self.camera.matrix)

            #render other 2
            self.ctx.fbo.depth_mask=True
            self.ctx.fbo.color_mask=(False,True,True,True)
        self.instance.render(moderngl.TRIANGLES)

        #bring back color mask or it will flicker idk
        self.ctx.fbo.color_mask=(True,True,True,True)
        if anaglyph:
            self.camera.position.x+=0.03
