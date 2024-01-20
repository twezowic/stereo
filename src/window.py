from typing import Any
from moderngl_window.context.base import KeyModifiers
import moderngl_window.resources
import moderngl_window.scene
import moderngl
from camera import PerspectiveCamera, StereoCamera, StereoCameraComponent
from pyrr import matrix44
import os
import pywavefront #for pipreqs
from PIL import Image
import math

from phong_window import PhongWindow

moderngl_window.resources.register_dir(os.path.dirname(os.path.realpath(__file__))+'/../resources')

class GkomApp(PhongWindow):
    title = "Renderer stereo"
    gl_version = (3, 3)

    def __init__(self, ctx, wnd, timer):
        super().__init__(ctx,wnd,timer)
        #perspective setup
        self.perspective_camera = PerspectiveCamera(self.wnd.keys,fov=45.0,aspect_ratio=self.wnd.aspect_ratio,near=0.1,far=1000.0)
        self.perspective_camera.set_position(0,0,5)

        #stereo setup
        left_camera = StereoCameraComponent(self.wnd.keys, fov=45.0, aspect_ratio=self.wnd.aspect_ratio/2, near=0.1, far=1000.0)
        left_camera.set_position(0, 0, 5)

        right_camera = StereoCameraComponent(self.wnd.keys, fov=45.0, aspect_ratio=self.wnd.aspect_ratio/2, near=0.1, far=1000.0)
        right_camera.set_position(0, 0, 5)

        self.stereo_camera = StereoCamera(left_camera, right_camera,eye_distance=0.9945*2,convergence=1)


        self.cameras = {'stereo':self.stereo_camera, 'perspective':self.perspective_camera}

        #setup active camera
        self.camera_type = 'perspective'

        #others
        self.wnd.mouse_exclusivity = True

        self.anaglyph = False
        self.przelot = False


    def key_event(self, key, action, modifiers):
        if key == self.wnd.keys.SPACE and action == self.wnd.keys.ACTION_PRESS:
            self.toggle_camera_type()
        elif key == self.wnd.keys.M and action == self.wnd.keys.ACTION_PRESS:
            self.save_image()

        elif key == self.wnd.keys.O and action == self.wnd.keys.ACTION_PRESS and not self.przelot:
            self.anaglyph = not self.anaglyph
        elif key == self.wnd.keys.P and action == self.wnd.keys.ACTION_PRESS and not self.anaglyph:
            self.przelot = not self.przelot

        elif key == self.wnd.keys.K and action == self.wnd.keys.ACTION_PRESS:
            self.cameras['stereo'].narrow()
        elif key == self.wnd.keys.L and action == self.wnd.keys.ACTION_PRESS:
            self.cameras['stereo'].extend()

        elif key == self.wnd.keys.R and action == self.wnd.keys.ACTION_PRESS:
            self.cameras['stereo'].modify_convergence()
        elif key == self.wnd.keys.T and action == self.wnd.keys.ACTION_PRESS:
            self.cameras['stereo'].modify_convergence(isadd=True)

        else:
            for camera in self.cameras.values():
                camera.key_input(key, action, modifiers)

        return super().key_event(key, action, modifiers)

    def save_image(self):
        fbo = self.ctx.simple_framebuffer(self.wnd.size, components=3)
        fbo.use()
        self.render(0, 0)
        pixels = fbo.read(components=3)

        image = Image.frombytes("RGB", self.wnd.size, pixels)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        if self.anaglyph and self.camera_type == 'perspective':
            image.save("anaglyph.png")
        elif self.camera_type == 'stereo':
            image.save("image.png")
            width, height= fbo.size
            self.crop_camera_image(width, height)
        #TODO przelot if self.przelot and self.camera_type == 'perspective':

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
            self.cameras[self.camera_type].setup_eye_distance(
                self.cameras['perspective'].position)
        else:
            self.camera_type = 'perspective'
            self.cameras[self.camera_type].setup_eye_distance(
                self.cameras['stereo'].left_camera.position,
                self.cameras['stereo'].right_camera.position
                )


    def mouse_drag_event(self, x, y, dx, dy):
        for camera in self.cameras.values():
            camera.rot_state(dx, dy)
        return super().mouse_drag_event(x, y, dx, dy)

    def render(self, time, frametime):
        if self.camera_type == 'stereo':
            self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
            self.ctx.clear(0.2, 0.2, 0.2, 0.0)

            # Set left eye
            self.cameras['stereo'].left_camera.look_at([0.1,0.0,0.0])
            self.camera_pos.write(self.cameras['stereo'].left_camera.position.astype('float32'))
            self.program["projection"].write(self.cameras['stereo'].left_camera.projection.matrix)
            self.program["view"].write(self.cameras['stereo'].left_camera.matrix)

            # Render left eye
            self.ctx.viewport = (0, 0, self.wnd.buffer_width // 2, self.wnd.buffer_height)
            self.instance.render(moderngl.TRIANGLES)

            # Set right eye
            self.cameras['stereo'].right_camera.look_at([0.1, 0.0, 0.0])
            self.camera_pos.write(self.cameras['stereo'].right_camera.position.astype('float32'))
            self.program["projection"].write(self.cameras['stereo'].right_camera.projection.matrix)
            self.program["view"].write(self.cameras['stereo'].right_camera.matrix)

            # Render right eye
            self.ctx.viewport = (self.wnd.buffer_width // 2, 0, self.wnd.buffer_width // 2, self.wnd.buffer_height)
            self.instance.render(moderngl.TRIANGLES)

            self.ctx.viewport = (0, 0, self.wnd.buffer_width, self.wnd.buffer_height)
        else:
            # print(self.cameras[2].position)
            # print(self.cameras[2].dir)
            self.cameras['perspective'].look_at([0.1,0.0,0.0])
            self.camera_pos.write(self.cameras['perspective'].position.astype('float32')) # how to lose 2 hours debugging
            self.program["projection"].write(self.cameras['perspective'].projection.matrix)
            self.program["view"].write(self.cameras['perspective'].matrix)

            self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
            self.ctx.clear(0.2, 0.2, 0.2, 0.0)
            #render red
            if self.anaglyph:
                self.ctx.fbo.color_mask=(True,False,False,True)
                self.instance.render(moderngl.TRIANGLES)

                # move camera
                self.cameras['perspective'].position.x-=0.03
                self.camera_pos.write(self.cameras['perspective'].position.astype('float32')) # how to lose 2 hours debugging
                self.program["projection"].write(self.cameras['perspective'].projection.matrix)
                self.program["view"].write(self.cameras['perspective'].matrix)

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
                self.cameras['perspective'].position.x+=0.03

    #def resize(self, w, h):
        #print("resize")
        #self.projection = matrix44.perspective_projection(45, self.aspect_ratio, 1, 50)

GkomApp.run()