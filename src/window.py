from typing import Any
from moderngl_window.context.base import KeyModifiers
import moderngl_window.resources
import moderngl_window.scene
import moderngl
from camera import PerspectiveCamera, StereoCamera
from pyrr import matrix44
import os
import pywavefront #for pipreqs
from PIL import Image

from phong_window import PhongWindow

moderngl_window.resources.register_dir(os.path.dirname(os.path.realpath(__file__))+'/../resources')

class GkomApp(PhongWindow):
    title = "Renderer stereo"
    gl_version = (3, 3)

    def __init__(self, ctx, wnd, timer):
        super().__init__(ctx,wnd,timer)
        #perspective setup
        self.perspecitve_camera = PerspectiveCamera(self.wnd.keys,fov=45.0,aspect_ratio=self.wnd.aspect_ratio,near=0.1,far=1000.0)
        self.perspecitve_camera.set_position(0,0,5)

        #stereo setup
        self.left_camera = StereoCamera(self.wnd.keys, fov=45.0, aspect_ratio=self.wnd.aspect_ratio/2, near=0.1, far=1000.0)
        self.left_camera.set_position(0, 0, 5)

        self.right_camera = StereoCamera(self.wnd.keys, fov=45.0, aspect_ratio=self.wnd.aspect_ratio/2, near=0.1, far=1000.0)
        self.right_camera.set_position(0, 0, 5)

        self.cameras = [self.left_camera, self.right_camera]

        #setup active camera
        self.camera_type = 'perspective'
        self.camera = self.perspecitve_camera

        #others
        self.camera.set_position(0,0,5)
        self.camera.mouse_sensitivity=0.3

        self.wnd.mouse_exclusivity = True

        self.anaglyph = True


    def key_event(self, key, action, modifiers):
        if self.camera_type == 'stereo':
            for camera in self.cameras:
                self.camera = camera
                self.camera.key_input(key, action, modifiers)
        else:
             self.camera.key_input(key,action,modifiers)
        if key == self.wnd.keys.SPACE and action == self.wnd.keys.ACTION_PRESS:
            self.toggle_camera_type()
        elif key == self.wnd.keys.M and action == self.wnd.keys.ACTION_PRESS:
            if self.camera_type == 'stereo':
                self.save_image(double=True)
            else:
                self.save_image(anaglyph=True)

        return super().key_event(key, action, modifiers)

    def save_image(self, anaglyph=False, double=False, przelot=False):
        fbo = self.ctx.simple_framebuffer(self.wnd.size, components=3)
        fbo.use()
        self.render(0, 0)
        pixels = fbo.read(components=3)

        image = Image.frombytes("RGB", self.wnd.size, pixels)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        print(double)

        if anaglyph:
            image.save("anaglyph.png")
        elif double:
            image.save("image.png")
            width, height= fbo.size
            self.crop_camera_image(width, height)
        #TODO przelot

    def crop_camera_image(self,width, height):
        image_path = "image.png"
        image = Image.open(image_path)

        width, height = image.size

        left_camera = image.crop((0, 0, width // 2, height))
        left_camera.save("left_camera.png")

        right_camera = image.crop((width // 2, 0, width, height))
        right_camera.save("right_camera.png")
        os.remove(image_path)

    def toggle_camera_type(self):
        if self.camera_type == 'perspective':
            self.camera_type = 'stereo'
            self.camera = self.perspecitve_camera
        else:
            self.camera_type = 'perspective'
            self.camera = self.left_camera

    def mouse_drag_event(self, x, y, dx, dy):
        if self.camera_type == 'stereo':
            for camera in self.cameras:
                self.camera = camera
                self.camera.rot_state(dx, dy)
        else:
            self.camera.rot_state(dx,dy)
        return super().mouse_drag_event(x, y, dx, dy)

    def render(self, time, frametime):
        if self.camera_type == 'stereo':
            self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
            self.ctx.clear(0.2, 0.2, 0.2, 0.0)

            # Set left eye
            self.camera = self.left_camera
            self.camera.look_at([0.1,0.0,0.0])
            self.camera_pos.write(self.camera.position.astype('float32'))
            self.program["projection"].write(self.camera.projection.matrix)
            self.program["view"].write(self.camera.matrix)

            # Render left eye
            self.ctx.viewport = (0, 0, self.wnd.buffer_width // 2, self.wnd.buffer_height)
            self.instance.render(moderngl.TRIANGLES)

            # Set right eye
            self.camera = self.right_camera
            self.camera.look_at([0.1, 0.0, 0.0])
            self.camera_pos.write(self.camera.position.astype('float32'))
            self.program["projection"].write(self.camera.projection.matrix)
            self.program["view"].write(self.camera.matrix)

            # Render right eye
            self.ctx.viewport = (self.wnd.buffer_width // 2, 0, self.wnd.buffer_width // 2, self.wnd.buffer_height)
            self.instance.render(moderngl.TRIANGLES)

            self.ctx.viewport = (0, 0, self.wnd.buffer_width, self.wnd.buffer_height)
        else:
            # print(self.camera.position)
            # print(self.camera.dir)
            self.camera = self.perspecitve_camera
            self.camera.look_at([0.1,0.0,0.0])
            self.camera_pos.write(self.camera.position.astype('float32')) # how to lose 2 hours debugging
            self.program["projection"].write(self.camera.projection.matrix)
            self.program["view"].write(self.camera.matrix)

            self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
            self.ctx.clear(0.2, 0.2, 0.2, 0.0)
            #render red
            if self.anaglyph:
                self.ctx.fbo.color_mask=(True,False,False,True)
                self.instance.render(moderngl.TRIANGLES)

                # move camera
                self.camera.position.x-=0.03
                self.camera_pos.write(self.camera.position.astype('float32')) # how to lose 2 hours debugging
                self.program["projection"].write(self.camera.projection.matrix)
                self.program["view"].write(self.camera.matrix)

                #render other 2
                # clear depth buffer, but dont touch color buffer!!
                self.ctx.fbo.color_mask=(False,False,False,False)
                self.ctx.fbo.clear(depth=1)

                # now work on the other 2 channels
                self.ctx.fbo.color_mask=(False,True,True,True)
            self.instance.render(moderngl.TRIANGLES)

            #bring back color mask or it will flicker idk
            self.ctx.fbo.color_mask=(True,True,True,True)
            if self.anaglyph:
                self.camera.position.x+=0.03

    #def resize(self, w, h):
        #print("resize")
        #self.projection = matrix44.perspective_projection(45, self.aspect_ratio, 1, 50)

GkomApp.run()