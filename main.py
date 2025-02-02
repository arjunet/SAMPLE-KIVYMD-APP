# MUST BE AT VERY TOP
from kivy.config import Config
Config.set('kivy', 'video', 'ffpyplayer')
Config.set('kivy', 'log_enable', '1')
Config.set('kivy', 'log_level', 'debug')

import random
import os
import traceback
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.video import Video
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Rectangle
from kivy.animation import Animation
from kivy.clock import Clock, mainthread
from kivy.utils import platform

# Android-specific imports for ExoPlayer
if platform == "android":
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    Uri = autoclass('android.net.Uri')

class ImageButton(Button):
    def __init__(self, source, **kwargs):
        super().__init__(**kwargs)
        self.source = source
        self.background_normal = ''
        self.background_color = (1, 1, 1, 0)
        self.color = kwargs.get('color', (1, 1, 1, 1))
        self.bind(pos=self.update_rect, size=self.update_rect)
        with self.canvas.before:
            self.rect = Rectangle(source=self.source, pos=self.pos, size=self.size)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class VideoPlayerScreen(Screen):
    def __init__(self, stream_url, **kwargs):
        super(VideoPlayerScreen, self).__init__(**kwargs)
        self.stream_url = stream_url
        self.play_stream()

    def play_stream(self):
        if platform == "android":
            intent = Intent()
            intent.setAction(Intent.ACTION_VIEW)
            intent.setDataAndType(Uri.parse(self.stream_url), "video/*")
            intent.putExtra("force_fullscreen", True)
            current_activity = PythonActivity.mActivity
            current_activity.startActivity(intent)
        else:
            self.add_widget(Label(text="ExoPlayer only works on Android!"))

class MyGrid(Screen):
    background_image = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = GridLayout(cols=2)
        self.video_popup = None

        #  Correct Streams Added
        channels = {
            "Florida ABC": "https://apollo.production-public.tubi.io/live/ac-wftv.m3u8",
            "Florida CBS": "https://video.tegnaone.com/wtsp/live/v1/master/f9c1bf9ffd6ac86b6173a7c169ff6e3f4efbd693/WTSP-Production/live/index.m3u8",
            "New York ABC": "https://content.uplynk.com/ext/72750b711f704e4a94b5cfe6dc99f5e1/080421-wabc-ctv-eveningupdate-vid.m3u8",
            "New York CBS": "https://content.uplynk.com/channel/ext/72750b711f704e4a94b5cfe6dc99f5e1/wabc_24x7_news.m3u8"
        }

        for name, url in channels.items():
            btn = Button(text=name, font_size=20, size_hint_y=None, height=100)
            btn.bind(on_press=lambda instance, stream_url=url: self.play_stream(stream_url))
            self.layout.add_widget(btn)

        self.add_widget(self.layout)

    def play_stream(self, stream_url):
        self.manager.add_widget(VideoPlayerScreen(name="video", stream_url=stream_url))
        self.manager.current = "video"

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MyGrid(name='grid'))
        return sm

if __name__ == '__main__':
    MyApp().run()
