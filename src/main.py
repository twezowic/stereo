import moderngl_window

class GkomApp(moderngl_window.WindowConfig):
    gl_version = (3, 3)

    def render(self, time, frametime):
        self.ctx.clear(1.0, 0.0, 0.0, 0.0)

GkomApp.run()