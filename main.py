from kivy.app import App
from kivy.core.image import Texture
from kivy.graphics import Color, Rectangle
from kivy.uix.floatlayout import FloatLayout

from kivy.config import Config
Config.set('modules', 'monitor', '')
Config.set('modules', 'showborder', '')

from kivy.utils import platform

if platform == 'android':
    from android.permissions import request_permissions, Permission, check_permission

from kivy.core.camera import Camera as CoreCamera, CameraBase
from kivy.uix.image import Image
from kivy.properties import NumericProperty, ListProperty, BooleanProperty, ObjectProperty
from kivy.core.window import Window
import numpy as np

from kivy.lang import Builder

Builder.load_string('''
<CameraControl>:
    resolution: [2190, 1080]
    allow_stretch: True
    
    canvas.before:
        PushMatrix
        Rotate:
            angle: -90 if app.isAndroid else 0
            origin: self.center
    canvas.after:
        PopMatrix
''')


class CameraControl(Image):
    index = NumericProperty(-1)
    play = BooleanProperty(True)
    resolution = ListProperty([-1, -1])

    def __init__(self, **kwargs):
        super(CameraControl, self).__init__(**kwargs)
        self.index = max(self.index, 0)
        self._camera = None

        on_change = self._on_change
        self.bind(index=on_change)
        self.bind(resolution=on_change)

        self._on_change()

    def _on_change(self, *l):
        if self.index < 0: #or self.resolution[0] < 0:
            return
        self._camera : CameraBase = CoreCamera(index=self.index, size=self.size, resolution=self.resolution)

        if self.play:
            self._camera.start()
            self._camera.bind(on_texture=self.update)

    def update(self, *l):
        self.canvas.ask_update()
        print(f"Window = {Window.size}")
        print(f"Widget = {self.size}")
        print(f"Image = {self.norm_image_size}")

        if not self.texture:
            self.texture = Texture.create(size=self._camera.texture.size, colorfmt=self._camera.texture.colorfmt)
            self.texture.flip_vertical()
        self.texture.blit_buffer(self._camera.texture.pixels, colorfmt=self._camera.texture.colorfmt)

    def stop(self):
        self._camera.stop()

class TestCamera(App):
    title = 'Scan Camera'
    isAndroid = False

    def build(self):
        if platform == 'android':
            request_permissions([Permission.CAMERA])
            self.isAndroid = True
        return CameraControl()

    def on_stop(self):
        self.root.stop()

if __name__ == '__main__':
    TestCamera().run()
