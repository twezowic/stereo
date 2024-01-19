from moderngl_window.scene import KeyboardCamera

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