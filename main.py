import kivy
from kivy.config import Config
from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture

Config.set('modules', 'monitor', '')

from kivy.app import App
from kivy.uix.image import Image
from kivy.core.camera import Camera as CoreCamera
from kivy.properties import NumericProperty, ListProperty, BooleanProperty, ObjectProperty
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.utils import platform
import numpy as np

if platform == 'android':
    from android.permissions import request_permissions, Permission, check_permission

Builder.load_string('''
#: import Window kivy.core.window.Window
<ScanCamera>:

<BarcWin>:
    ScanCamera:
        pos_hint: {'top': 0.9, 'right': 1}
        size_hint: [1, 0.8]
        canvas.before:
            PushMatrix
            Rotate:
                angle: -90
                origin: self.center
        canvas.after:
            PopMatrix
            Line:
                width: 2.
                rectangle: (self.x + 40, self.y + 40, self.width/1.1, self.height/1.12)
    ToggleButton:
        id: show_bcode
        pos_hint: {'bottom': 1, 'right': 1}
        size_hint: [1, 0.1]
        color: (1,1,1,1)
        background_color: (0,0,0,0)
        background_normal: ''
        canvas.before:
            Color:
                rgba: (.18,.36,.61,1) if self.state=='down' else (0,0,0,1) 
            Rectangle:
                pos: self.pos
                size: self.size
        text: 'Hier kom die barcode...'
''')


class BarcWin(FloatLayout):
    cam_cam = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(BarcWin, self).__init__(**kwargs)
        self.cam_cam = ScanCamera()

    def accept_in(self):
        print('In')

    def accept_out(self):
        print('Out')


class ScanCamera(Image):
    play = BooleanProperty(True)
    index = NumericProperty(-1)
    resolution = ListProperty([1920, 1080])
    app_ini_ = ObjectProperty(None)

    def __init__(self, **kwargs):
        self._camera = None
        super(ScanCamera, self).__init__(**kwargs)
        if self.index == -1:
            self.index = 0
        on_index = self._on_index
        fbind = self.fbind
        fbind('index', on_index)
        fbind('resolution', on_index)
        on_index()
        self.app_ini_ = App.get_running_app()

    def on_tex(self, *l):
        self.canvas.ask_update()
        if self.texture:
            print(len(self.texture.pixels))
            mask : Texture = Texture.create(size=self.texture.size, colorfmt='rgba')
            texture = np.array(([255, 0, 0, 255] * (len(self.texture.pixels) // 8) + [0, 0, 0, 255] * (len(self.texture.pixels) // 8)), dtype='uint8').tostring()
            mask.blit_buffer(texture, colorfmt='rgba')
            Color(1, 1, 1, 1)
            Rectangle(texture=mask, size=self.texture.size)

    def _on_index(self, *largs):
        self._camera = None
        if self.index < 0:
            return
        if self.resolution[0] < 0 or self.resolution[1] < 0:
            return
        # first init of corecamera object
        if platform == 'android' and not check_permission(Permission.CAMERA):
            raise RuntimeError('Camera permission denied!')
        self._camera = CoreCamera(index=self.index,
                                  resolution=self.resolution, stopped=True, size=self.size)

        # when camera loads call _camera_loaded method to bind corecamera method with uix.image texture
        self._camera.bind(on_load=self._camera_loaded)
        if self.play:
            self._camera.start()
            self._camera.bind(on_texture=self.on_tex)

    def _camera_loaded(self, *largs):
        # bind camera texture with uix.image texture that is still equal to None
        self.texture = self._camera.texture

    def on_play(self, instance, value):
        if not self._camera:
            return
        if value:
            self._camera.start()
        else:
            self._camera.stop()


class TestCamera(App):
    title = 'Scan Camera'

    def build(self):
        if platform == 'android':
            request_permissions([Permission.CAMERA])
        return BarcWin()

    def on_stop(self):
        cc = ScanCamera()
        cc._camera.stop()
        print('Stop')

    def on_pause(self):
        return True

    def on_resume(self):
        pass

if __name__ == '__main__':
    TestCamera().run()