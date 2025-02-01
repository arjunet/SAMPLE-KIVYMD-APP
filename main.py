# MUST BE AT VERY TOP
from kivy.config import Config

Config.set('kivy', 'video', 'ffpyplayer')

import random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.video import Video
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Rectangle, Color
from kivy.animation import Animation
from kivy.clock import Clock


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
        super(MyGrid, self).__init__(**kwargs)
        self.layout = GridLayout(cols=2)
        with self.layout.canvas.before:
            self.bg = Rectangle(source=self.background_image if self.background_image else '',
                                pos=self.layout.pos, size=self.layout.size)
        self.layout.bind(pos=self.update_bg, size=self.update_bg)

        button_style = {
            'font_size': 60,
            'color': [0, 0, 0, 1],
            'background_color': (0, 0, 0, 0),
            'background_normal': '',
            'bold': True
        }

        self.Florida_ABC = Button(text="Florida ABC", **button_style)
        self.Florida_ABC.bind(on_press=self.button_pressed)
        self.layout.add_widget(self.Florida_ABC)

        self.Florida_CBS = Button(text="Florida CBS", **button_style)
        self.Florida_CBS.bind(on_press=self.button_pressed)
        self.layout.add_widget(self.Florida_CBS)

        self.NewYork_ABC = Button(text="New York ABC", **button_style)
        self.NewYork_ABC.bind(on_press=self.button_pressed)
        self.layout.add_widget(self.NewYork_ABC)

        self.NewYork_CBS = Button(text="New York CBS", **button_style)
        self.NewYork_CBS.bind(on_press=self.button_pressed)
        self.layout.add_widget(self.NewYork_CBS)

        self.video_popup = None
        self.add_widget(self.layout)

    def update_bg(self, *args):
        if hasattr(self, 'bg'):
            self.bg.pos = self.layout.pos
            self.bg.size = self.layout.size
            self.bg.source = self.background_image if self.background_image else ''

    def button_pressed(self, instance):
        anim = Animation(color=[1, 0, 0, 1], duration=0.5) + Animation(color=[0, 0, 0, 1], duration=0.5)
        anim.repeat = True
        anim.start(instance)
        Clock.schedule_once(lambda dt: self.stop_animation_and_call(instance), 3)

    def stop_animation_and_call(self, instance):
        Animation.cancel_all(instance)
        instance.color = [0, 0, 0, 1]
        if instance == self.Florida_ABC:
            self.FLABCCALL(instance)
        elif instance == self.Florida_CBS:
            self.FLCBSCALL(instance)
        elif instance == self.NewYork_ABC:
            self.NYABCCALL(instance)
        elif instance == self.NewYork_CBS:
            self.NYCBSCALL(instance)

    def play_stream(self, url):
        # Close existing popup
        if self.video_popup:
            self.video_popup.dismiss()

        try:
            # Create video widget with valid properties
            video = Video(
                source=url,
                state='play',
                options={'eos': 'loop'},
                size_hint=(1, 1),
                allow_stretch=True
            )

            # Create fullscreen container
            box = BoxLayout()
            box.add_widget(video)

            # Add close button
            close_btn = Button(
                text='X',
                size_hint=(None, None),
                size=(50, 50),
                pos_hint={'right': 0.95, 'top': 0.95}
            )

            # Create popup
            self.video_popup = Popup(
                title='',
                content=box,
                size_hint=(1, 1),
                auto_dismiss=False
            )

            close_btn.bind(on_release=self.video_popup.dismiss)
            box.add_widget(close_btn)

            self.video_popup.open()

        except Exception as e:
            print(f"Error playing stream: {e}")

    def FLABCCALL(self, instance):
        self.play_stream("https://apollo.production-public.tubi.io/live/ac-wftv.m3u8")

    def FLCBSCALL(self, instance):
        self.play_stream(
            "https://video.tegnaone.com/wtsp/live/v1/master/f9c1bf9ffd6ac86b6173a7c169ff6e3f4efbd693/WTSP-Production/live/index.m3u8?checkedby:iptvcat.com")

    def NYABCCALL(self, instance):
        self.play_stream(
            "https://content.uplynk.com/ext/72750b711f704e4a94b5cfe6dc99f5e1/080421-wabc-ctv-eveningupdate-vid.m3u8")

    def NYCBSCALL(self, instance):
        self.play_stream("https://content.uplynk.com/channel/ext/72750b711f704e4a94b5cfe6dc99f5e1/wabc_24x7_news.m3u8")


class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(Setup(name='setup'))
        sm.add_widget(ImageButtonScreen(name='image_button'))
        sm.add_widget(MyGrid(name='grid'))
        try:
            with open("User_data.txt", "r") as file:
                if file.read().strip():
                    sm.current = 'image_button'
                else:
                    sm.current = 'setup'
        except FileNotFoundError:
            sm.current = 'setup'
        return sm


if __name__ == "__main__":
    MyApp().run()
