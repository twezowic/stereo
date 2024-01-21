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
        self.cameras[self.camera_type].mouse_sensitivity=0.3
        self.eye_spacing = 0.1 # for 3d
        self.focus_angle = 0.7

        self.wnd.mouse_exclusivity = True

        self.anaglyph = True
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

        for camera in self.cameras.values():
            camera.key_input(key, action, modifiers)

        if key == self.wnd.keys.EQUAL and action == self.wnd.keys.ACTION_PRESS:
            self.focus_angle+=0.1
            print("focus angle:",self.focus_angle)
        if key == self.wnd.keys.MINUS and action == self.wnd.keys.ACTION_PRESS:
            self.focus_angle-=0.1
            print("focus angle:",self.focus_angle)

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

    def render_all_meshes(self):
        for mesh in self.scene.meshes:
            self.update_current_material(mesh)
            self.instance = mesh.vao.instance(self.program)
            self.instance.render(moderngl.TRIANGLES) 

    def mouse_drag_event(self, x, y, dx, dy):
        for camera in self.cameras.values():
            camera.rot_state(dx, dy)
        return super().mouse_drag_event(x, y, dx, dy)

    def render(self, time, frametime):
        self.ctx.fbo.color_mask=(True,True,True,True)
        self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
        self.ctx.clear(0.2, 0.2, 0.2, 0.0)

        if self.camera_type == 'stereo':

            # Set left eye
            self.cameras['stereo'].left_camera.look_at([0.1,0.0,0.0])
            self.camera_pos.write(self.cameras['stereo'].left_camera.position.astype('float32'))
            self.program["projection"].write(self.cameras['stereo'].left_camera.projection.matrix)
            self.program["view"].write(self.cameras['stereo'].left_camera.matrix)

            # Render left eye
            self.ctx.viewport = (0, 0, self.wnd.buffer_width // 2, self.wnd.buffer_height)
            self.render_all_meshes()

            # Set right eye
            self.cameras['stereo'].right_camera.look_at([0.1, 0.0, 0.0])
            self.camera_pos.write(self.cameras['stereo'].right_camera.position.astype('float32'))
            self.program["projection"].write(self.cameras['stereo'].right_camera.projection.matrix)
            self.program["view"].write(self.cameras['stereo'].right_camera.matrix)

            # Render right eye
            self.ctx.viewport = (self.wnd.buffer_width // 2, 0, self.wnd.buffer_width // 2, self.wnd.buffer_height)
            self.render_all_meshes()

            self.ctx.viewport = (0, 0, self.wnd.buffer_width, self.wnd.buffer_height)
        else:
            # print(self.camera.dir)
            self.camera = self.cameras["perspective"]
            #self.camera.look_at([0.1,0.0,0.0])
            #render red
            if self.anaglyph:

                # move camera to right eye
                self.camera.position.x-=self.camera.dir[2]*self.eye_spacing
                self.camera.position.z+=self.camera.dir[0]*self.eye_spacing
                # rotate to look at focus point
                self.camera.set_rotation(self.camera.yaw-self.focus_angle,self.camera.pitch)

                self.camera_pos.write(self.camera.position.astype('float32')) # how to lose 2 hours debugging
                self.program["projection"].write(self.camera.projection.matrix)
                self.program["view"].write(self.camera.matrix)

                self.ctx.fbo.color_mask=(True,False,False,True)
                self.render_all_meshes()

                #unrotate
                self.camera.set_rotation(self.camera.yaw+self.focus_angle,self.camera.pitch)
                # move camera to left eye
                self.camera.position.x+=2*self.camera.dir[2]*self.eye_spacing
                self.camera.position.z-=2*self.camera.dir[0]*self.eye_spacing

                # rotate for right eye
                self.camera.set_rotation(self.camera.yaw+self.focus_angle,self.camera.pitch)

                self.camera_pos.write(self.camera.position.astype('float32')) # how to lose 2 hours debugging
                self.program["projection"].write(self.camera.projection.matrix)
                self.program["view"].write(self.camera.matrix)

                #render other 2
                # clear depth buffer, but dont touch color buffer!!
                self.ctx.fbo.color_mask=(False,False,False,False)
                self.ctx.fbo.clear(depth=1)

                # now work on the other 2 channels
                self.ctx.fbo.color_mask=(False,True,True,True)

            self.render_all_meshes()
            if self.anaglyph:
                #unrotate
                self.camera.set_rotation(self.camera.yaw-self.focus_angle,self.camera.pitch)
                self.camera.position.x-=self.camera.dir[2]*self.eye_spacing
                self.camera.position.z+=self.camera.dir[0]*self.eye_spacing

                # rotate to normal angle

    #def resize(self, w, h):
        #print("resize")
        #self.projection = matrix44.perspective_projection(45, self.aspect_ratio, 1, 50)

GkomApp.run()