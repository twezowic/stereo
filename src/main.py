from typing import Any
from moderngl_window.context.base import KeyModifiers
import moderngl_window.resources
import moderngl_window.scene
import moderngl
from pyrr import matrix44
import os
import pywavefront #for pipreqs

moderngl_window.resources.register_dir(os.path.dirname(os.path.realpath(__file__))+'/../resources') 

class GkomApp(moderngl_window.WindowConfig):
    title = "Renderer stereo"
    gl_version = (3, 3)

    def __init__(self, ctx, wnd, timer):
        super().__init__(ctx,wnd,timer)
        self.objects = []
        self.camera = moderngl_window.scene.KeyboardCamera(self.wnd.keys,fov=45.0,aspect_ratio=self.wnd.aspect_ratio,near=0.1,far=1000.0)
        self.objects.append(self.load_scene('suzanne.obj'))
        self.camera.set_position(0,0,5)
        self.camera.mouse_sensitivity=0.3
    
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

        for o in self.objects:
            o.draw(self.camera.projection.matrix,self.camera.matrix)


GkomApp.run()