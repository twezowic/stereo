from moderngl_window.scene import KeyboardCamera

class PerspectiveCamera(KeyboardCamera):
    def __init__(self, keys, fov=45.0, aspect_ratio=1.0, near=0.1, far=1000.0):
        super().__init__(keys, fov=fov, aspect_ratio=aspect_ratio, near=near, far=far)

class StereoCamera(KeyboardCamera):
    def __init__(self, keys, fov=45.0, aspect_ratio=1.0, near=0.1, far=1000, eye_distance=1.0):
        super().__init__(keys, fov=fov, aspect_ratio=aspect_ratio, near=near, far=far)
        self.eye_distance = eye_distance