# MUST BE AT VERY TOP
from kivy.config import Config

Config.set('kivy', 'video', 'ffpyplayer')
Config.set('kivy', 'log_enable', '1')
Config.set('kivy', 'log_level', 'debug')

import random
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Rectangle, Color
from kivy.animation import Animation
from kivy.clock import Clock, mainthread
from jnius import autoclass
from kivy.core.window import Window
from kivy.logger import Logger


class FocusableChannelButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.default_text_color = (0, 0, 0, 1)
        self.focus_color = (1, 0.5, 0, 0.3)  # Orange highlight
        self.color = self.default_text_color

        with self.canvas.after:
            Color(*self.focus_color)
            self.focus_rect = Rectangle(
                pos=(self.x - 5, self.y - 5),
                size=(self.width + 10, self.height + 10),
                opacity=0
            )

        self.bind(
            pos=self.update_focus_rect,
            size=self.update_focus_rect,
            focus=self.on_focus
        )

    def update_focus_rect(self, *args):
        self.focus_rect.pos = (self.x - 5, self.y - 5)
        self.focus_rect.size = (self.width + 10, self.height + 10)

    def on_focus(self, instance, value):
        self.focus_rect.opacity = 1 if value else 0
        self.background_color = (1, 0.5, 0, 0.2) if value else (0, 0, 0, 0)


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
        message_label = Label(text="Please select a theme below")
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

        channels = [
            "Florida ABC", "Florida CBS",
            "New York ABC", "New York CBS"
        ]

        self.buttons = []
        for channel in channels:
            btn = FocusableChannelButton(
                text=channel,
                font_size=60,
                color=(0, 0, 0, 1),
                bold=True
            )
            btn.bind(on_press=self.play_channel)
            self.layout.add_widget(btn)
            self.buttons.append(btn)

        # Set focus navigation
        for i, btn in enumerate(self.buttons):
            btn.focus_next = {
                'up': self.buttons[i - 2] if i >= 2 else None,
                'down': self.buttons[i + 2] if i < len(self.buttons) - 2 else None,
                'left': self.buttons[i - 1] if i % 2 != 0 else None,
                'right': self.buttons[i + 1] if i % 2 == 0 else None
            }

        self.add_widget(self.layout)
        self.buttons[0].focus = True

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
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')

            intent = Intent()
            intent.setAction(Intent.ACTION_VIEW)
            intent.setDataAndType(Uri.parse(url), "video/*")

            current_activity = PythonActivity.mActivity
            current_activity.startActivity(intent)

        except Exception as e:
            error_msg = f"ERROR: {str(e)}"
            print(error_msg)


class MyApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(Setup(name='setup'))
        self.sm.add_widget(ImageButtonScreen(name='image_button'))
        self.sm.add_widget(MyGrid(name='grid'))

        try:
            with open("User_data.txt", "r") as file:
                self.sm.current = 'image_button' if file.read().strip() else 'setup'
        except FileNotFoundError:
            self.sm.current = 'setup'

        Window.bind(on_keyboard=self.on_keyboard)
        return self.sm

    def on_keyboard(self, window, key, *args):
        KEY_UP = 19
        KEY_DOWN = 20
        KEY_LEFT = 21
        KEY_RIGHT = 22
        KEY_ENTER = 23
        KEY_BACK = 4

        if key == KEY_BACK:
            self.handle_back()
            return True

        current = Window.focus_widget
        if not current:
            return False

        if key == KEY_ENTER:
            current.trigger_action(0.1)
            return True

        direction_map = {
            KEY_UP: 'up',
            KEY_DOWN: 'down',
            KEY_LEFT: 'left',
            KEY_RIGHT: 'right'
        }

        if key in direction_map:
            direction = direction_map[key]
            next_widget = getattr(current.focus_next, direction, None)
            if next_widget:
                current.focus = False
                next_widget.focus = True
                Window.focus_widget = next_widget
                return True

        return False

    def handle_back(self):
        if self.sm.current == 'image_button':
            self.sm.current = 'setup'
        elif self.sm.current == 'grid':
            self.sm.current = 'image_button'
        else:
            self.sm.current = 'setup'


if __name__ == "__main__":
    MyApp().run()
