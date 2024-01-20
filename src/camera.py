from moderngl_window.scene import KeyboardCamera
import math

class PerspectiveCamera(KeyboardCamera):
    def __init__(self, keys, fov=45.0, aspect_ratio=1.0, near=0.1, far=1000.0):
        super().__init__(keys, fov=fov, aspect_ratio=aspect_ratio, near=near, far=far)

    def setup_eye_distance(self, pos1, pos2):
        self.position.y = pos1.y
        self.position.z = pos1.z
        self.position.x = (pos1.x + pos2.x) / 2


class StereoCameraComponent(PerspectiveCamera):
    def __init__(self, keys, fov=45.0, aspect_ratio=1.0, near=0.1, far=1000):
        super().__init__(keys, fov=fov, aspect_ratio=aspect_ratio, near=near, far=far)


class StereoCamera():
    def __init__(self, left_camera, right_camera, eye_distance=5.0, convergence=0.0):
        self.left_camera = left_camera
        self.right_camera = right_camera
        self.convergence = convergence # w radianach/stopniach
        self.eye_distance = eye_distance

        self.setup_intersection()

    def key_input(self, key, action, modifiers):
        self.left_camera.key_input(key, action, modifiers)
        self.right_camera.key_input(key, action, modifiers)
    def rot_state(self, dx, dy):
        self.left_camera.rot_state(dx, dy)
        self.right_camera.rot_state(dx, dy)

    def setup_eye_distance(self, pos):
        self.left_camera.position.y = pos.y
        self.left_camera.position.z = pos.z
        self.left_camera.position.x = pos.x + self.eye_distance/2

        self.right_camera.position.y = pos.y
        self.right_camera.position.z = pos.z
        self.right_camera.position.x = pos.x - self.eye_distance/2

    def setup_intersection(self):
        cos = (self.eye_distance / 2) / self.convergence
        angle = 90 - math.degrees(math.acos(cos))
        print(angle)
        print(self.left_camera.yaw)
        self.left_camera.yaw -= angle
        self.right_camera.yaw += angle
        print('left')
        print(self.left_camera.yaw)
        return angle

    def modify_convergence(self,isadd=False):
        if isadd:
            self.left_camera.yaw += 1
            self.right_camera.yaw -= 1
        else:
            self.left_camera.yaw -= 1
            self.right_camera.yaw += 1

    def narrow(self):
        if self.left_camera.position.x > self.right_camera.position.x:
            self.left_camera.position.x -= 1
            self.right_camera.position.x += 1
            print(self.left_camera.position.x)
            print(self.right_camera.position.x)

    def extend(self):
        self.left_camera.position.x += 1
        self.right_camera.position.x -= 1

if __name__ == '__main__':
    ca = StereoCamera('a','b',8,4*math.sqrt(2))
    print(ca.setup_intersection())