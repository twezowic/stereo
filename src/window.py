from typing import Any
from moderngl_window.context.base import KeyModifiers
import moderngl_window.resources
import moderngl_window.scene
import moderngl
from pyrr import matrix44
import os
import pywavefront #for pipreqs
import shader_utils
import scene_settings
import numpy as np

moderngl_window.resources.register_dir(os.path.dirname(os.path.realpath(__file__))+'/../resources') 

class GkomApp(moderngl_window.WindowConfig):
    title = "Renderer stereo"
    gl_version = (3, 3)

    def __init__(self, ctx, wnd, timer):
        super().__init__(ctx,wnd,timer)
        self.program = self.get_program()
        self.init_shaders_variables()
        self.scene = self.load_scene('suzanne.obj')
        self.lights = scene_settings.get_lights();
        self.instance = self.scene.root_nodes[0].mesh.vao.instance(self.program)
        self.camera = moderngl_window.scene.KeyboardCamera(self.wnd.keys,fov=45.0,aspect_ratio=self.wnd.aspect_ratio,near=0.1,far=1000.0)
        self.camera.set_position(0,0,5)
        self.camera.mouse_sensitivity=0.3

    def get_program(self):
        shaders = shader_utils.get_shaders(os.path.dirname(os.path.realpath(__file__))+'/../resources/shader/')
        program = self.ctx.program(fragment_shader=shaders['phong'].fragment_shader, vertex_shader=shaders['phong'].vertex_shader)
        return program

    def init_shaders_variables(self):
        # get projection and view matrix references
        self.proj_matrix = self.program["projection"]
        self.view_matrix = self.program["view"]


        # make point lights form config
        lights_nparrays = scene_settings.get_lights()
        for idx,point_light in enumerate(lights_nparrays):
            self.program[f"point_lights[{idx}].pos"].write(point_light.pos)
            self.program[f"point_lights[{idx}].color"].write(point_light.color)
        self.program["light_count"].value=len(lights_nparrays)
        
        # ambient lighting settings
        colors = [x.color for x in lights_nparrays]
        self.program["ambient_color"].write(np.average(colors,axis=0))
        self.program["ambient_intensity"].value=len(lights_nparrays)*0.1;


    
    def key_event(self, key: Any, action: Any, modifiers: KeyModifiers):
        self.camera.key_input(key,action,modifiers)
        return super().key_event(key, action, modifiers)
    
    def mouse_drag_event(self, x, y, dx, dy):
        self.camera.rot_state(dx,dy)

    #def resize(self, w, h):
        #print("resize")
        #self.projection = matrix44.perspective_projection(45, self.aspect_ratio, 1, 50)

    def render(self, time, frametime):
        self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
        self.ctx.clear(0.2, 0.2, 0.2, 0.0)

        print(self.camera.position)
        print(self.camera.dir)
        self.camera.look_at([0.1,0.0,0.0])

        
        self.proj_matrix.write(self.camera.projection.matrix)
        self.view_matrix.write(self.camera.matrix)
        self.instance.render(moderngl.TRIANGLES)

GkomApp.run()