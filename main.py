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

# NEW: Import Pyjnius to access Android native classes.
from jnius import autoclass


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


class Setup(Screen):
    def __init__(self, **kwargs):
        super(Setup, self).__init__(**kwargs)
        layout = GridLayout(cols=2)
        layout.add_widget(Label(text="Please enter your name here --->"))
        self.name_input = TextInput(multiline=False)
        layout.add_widget(self.name_input)
        self.twoFA_code = random.randint(100000, 999999)
        layout.add_widget(Label(
            text=f"Type in the code ---> {self.twoFA_code}"))
        self.code_input = TextInput(multiline=False)
        layout.add_widget(self.code_input)
        self.submit = Button(text="Save")
        self.submit.bind(on_press=self.pressed)
        layout.add_widget(self.submit)
        self.add_widget(layout)

    def pressed(self, instance):
        name = self.name_input.text
        user_code = self.code_input.text
        with open("User_data.txt", "w") as file:
            file.write(name)
        try:
            user_code = int(user_code)
        except ValueError:
            self.show_popup("Error", "Invalid input. Please enter numbers only.")
            return
        if user_code == self.twoFA_code:
            self.show_popup("Success", "Saved Successfully!")
            self.manager.current = 'image_button'
        else:
            self.show_popup("Error", "Incorrect code. Please try again.")

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        label = Label(text=message)
        close_button = Button(text="OK", size_hint=(1, 0.5))
        content.add_widget(label)
        content.add_widget(close_button)
        popup = Popup(title=title, content=content, size_hint=(0.6, 0.4), auto_dismiss=False)
        close_button.bind(on_release=popup.dismiss)
        popup.open()


class ImageButtonScreen(Screen):
    def __init__(self, **kwargs):
        super(ImageButtonScreen, self).__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        mode_row = BoxLayout(orientation='horizontal', spacing=10)

        modes = [
            ('Galaxy Mode', 'nebula.jpg'),
            ('Rainy Mode', 'rain.jpg'),
            ('Sunny Mode', 'sunny.jpg'),
            ('Western Mode', 'west.jpg')
        ]

        for text, source in modes:
            btn = ImageButton(
                source=source,
                text=text,
                font_size=40,
                bold=True,
                color=(0, 0, 0, 1),
                size_hint=(1, 1)
            )
            btn.bind(on_press=self.set_background_and_transition)
            mode_row.add_widget(btn)

        main_layout.add_widget(mode_row)
        self.add_widget(main_layout)

    def on_enter(self):
        self.show_theme_popup()

    def show_theme_popup(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        message_label = Label(text="Please select a theme below to proceed:")
        close_button = Button(text="OK", size_hint=(1, 0.5))
        content.add_widget(message_label)
        content.add_widget(close_button)

        popup = Popup(title="Theme",
                      content=content,
                      size_hint=(0.6, 0.4),
                      auto_dismiss=False)
        close_button.bind(on_release=popup.dismiss)
        popup.open()

    def set_background_and_transition(self, instance):
        MyGrid.background_image = instance.source
        self.manager.current = 'grid'


class MyGrid(Screen):
    background_image = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = GridLayout(cols=2)
        self.video_popup = None

        # Channel buttons
        channels = [
            "Florida ABC", "Florida CBS",
            "New York ABC", "New York CBS"
        ]

        for channel in channels:
            btn = Button(text=channel, font_size=60,
                         background_color=(0, 0, 0, 0),
                         color=(0, 0, 0, 1),
                         bold=True)
            btn.bind(on_press=self.play_channel)
            self.layout.add_widget(btn)

        self.add_widget(self.layout)

    def on_pre_enter(self):
        with self.layout.canvas.before:
            self.bg = Rectangle(source=self.background_image or '',
                                size=self.layout.size, pos=self.layout.pos)
        self.layout.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        self.bg.pos = self.layout.pos
        self.bg.size = self.layout.size

    def play_channel(self, instance):
        anim = (Animation(color=(1, 0, 0, 1), duration=0.5) +
                Animation(color=(0, 0, 0, 1), duration=0.5))
        anim.repeat = True
        anim.start(instance)
        Clock.schedule_once(lambda dt: self.start_stream(instance), 2)

    def start_stream(self, instance):
        Animation.cancel_all(instance)
        instance.color = (0, 0, 0, 1)

        streams = {
            "Florida ABC": "https://apollo.production-public.tubi.io/live/ac-wftv.m3u8",
            "Florida CBS": "https://video.tegnaone.com/wtsp/live/v1/master/f9c1bf9ffd6ac86b6173a7c169ff6e3f4efbd693/WTSP-Production/live/index.m3u8",
            "New York ABC": "https://content.uplynk.com/ext/72750b711f704e4a94b5cfe6dc99f5e1/080421-wabc-ctv-eveningupdate-vid.m3u8",
            "New York CBS": "https://content.uplynk.com/channel/ext/72750b711f704e4a94b5cfe6dc99f5e1/wabc_24x7_news.m3u8"
        }

        self.play_stream(streams[instance.text])

    @mainthread
    def play_stream(self, url):
        try:
            # Cleanup previous instances
            if self.video_popup:
                self.video_popup.dismiss()
                self.video_popup = None

            # --- BEGIN MODIFICATION: Use Android's native VideoView ---
            # Access native Android classes
            VideoView = autoclass('android.widget.VideoView')
            Uri = autoclass('android.net.Uri')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity

            # Create the native VideoView and set it up
            native_video = VideoView(activity)
            video_uri = Uri.parse(url)
            native_video.setVideoURI(video_uri)
            native_video.requestFocus()
            native_video.start()

            # Add the native VideoView to the activity's view hierarchy in full screen
            LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')
            params = LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT)
            activity.addContentView(native_video, params)
            # --- END MODIFICATION ---

            # Create an overlay popup with a close button to dismiss the native player
            content = BoxLayout()
            close_btn = Button(
                text='X',
                size_hint=(None, None),
                size=(50, 50),
                pos_hint={'right': 0.95, 'top': 0.95},
                background_color=(1, 0, 0, 1)
            )
            self.video_popup = Popup(
                title='',
                content=content,
                size_hint=(1, 1),
                auto_dismiss=False,
                separator_height=0
            )
            content.add_widget(close_btn)
            close_btn.bind(on_release=lambda *args: self.close_native_video(native_video))
            self.video_popup.open()

        except Exception as e:
            error_msg = f"ANDROID ERROR: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            # Write to external storage for debugging
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
            log_dir = "/sdcard/stream_app_logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            with open(os.path.join(log_dir, "error.log"), "a") as f:
                f.write(error_msg + "\n")

    def close_native_video(self, native_video):
        try:
            # Remove the native VideoView from the view hierarchy
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            parent = native_video.getParent()
            if parent:
                parent.removeView(native_video)
            if self.video_popup:
                self.video_popup.dismiss()
                self.video_popup = None
        except Exception as e:
            print("Error closing native video:", e)


class MyApp(App):
    def build(self):
        sm = ScreenManager()

        # Only go through Setup if "User_data.txt" is empty or does not exist.
        if os.path.exists("User_data.txt") and os.path.getsize("User_data.txt") > 0:
            sm.add_widget(ImageButtonScreen(name='image_button'))
        else:
            sm.add_widget(Setup(name='setup'))

        sm.add_widget(MyGrid(name='grid'))
        return sm


if __name__ == "__main__":
    MyApp().run()
