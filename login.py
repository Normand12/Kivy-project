from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from main import MainScreen


class RoundedTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._initialize_properties()
        self._setup_canvas()
        self.bind(focused=self.on_focused)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def _initialize_properties(self):
        self.padding = [20, 10, 20, 10]
        self.size_hint = (None, None)
        self.width = dp(250)
        self.height = dp(40)
        self.multiline = False
        self.foreground_color = (0, 0, 0, 1)
        self.cursor_color = (0, 0, 0, 1)
        self.selection_color = (0.2, 0.6, 1, 0.3)
        self.hint_text_color = (0.5, 0.5, 0.5, 1)
        self.background_color = [0, 0, 0, 0]
        self.background_active = ''
        self.background_normal = ''

    def _setup_canvas(self):
        with self.canvas.before:
            self.background_color_instruction = Color(0.95, 0.95, 0.95, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_focused(self, instance, value):
        self.background_color_instruction.rgba = (1, 1, 1, 1) if value else (0.95, 0.95, 0.95, 1)

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._initialize_properties()
        self._setup_canvas()
        self.bind(pos=self.update_rect, size=self.update_rect)

    def _initialize_properties(self):
        self.background_normal = ''
        self.background_color = (0.2, 0.6, 1, 1)
        self.size_hint = (None, None)
        self.width = dp(200)
        self.height = dp(40)

    def _setup_canvas(self):
        with self.canvas.before:
            Color(*self.background_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        self.main_layout = self._create_main_layout()
        center_container = self._create_center_container()
        self._add_welcome_label(center_container)
        self._create_login_form(center_container)
        self._add_login_button(center_container)
        self._finalize_layout(center_container)

    def _create_main_layout(self):
        main_layout = BoxLayout(orientation='vertical', spacing=20)
        with main_layout.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            self.rect = RoundedRectangle(pos=main_layout.pos, size=main_layout.size)
            main_layout.bind(pos=self.update_rect, size=self.update_rect)
        return main_layout

    def _create_center_container(self):
        container = BoxLayout(
            orientation='vertical',
            spacing=20,
            size_hint_y=None,
            height=dp(300),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        return container

    def _add_welcome_label(self, container):
        welcome_label = Label(
            text="Welcome to Sobotify",
            font_size=24,
            size_hint_y=None,
            height=dp(50),
            color=(0.2, 0.2, 0.2, 1)
        )
        container.add_widget(welcome_label)

    def _create_login_form(self, container):
        form_container = BoxLayout(
            orientation='vertical',
            spacing=15,
            size_hint_y=None,
            height=dp(150),
            pos_hint={'center_x': 0.5}
        )

        self.username_input = self._create_input_field("Username", self.on_username_enter)
        self.password_input = self._create_input_field("Password", self.verify_credentials, is_password=True)

        form_container.add_widget(self.username_input)
        form_container.add_widget(self.password_input)
        container.add_widget(form_container)

    def _create_input_field(self, label_text, validate_callback, is_password=False):
        container = BoxLayout(
            orientation='vertical',
            spacing=5,
            size_hint_y=None,
            height=dp(65),
            pos_hint={'center_x': 0.5},
            size_hint_x=None,
            width=dp(250)
        )
        
        label = Label(
            text=label_text,
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            height=dp(20)
        )
        
        input_field = RoundedTextInput(
            hint_text=f"Enter {label_text.lower()}",
            password=is_password,
            multiline=False,
            write_tab=False,
            on_text_validate=validate_callback
        )
        
        container.add_widget(label)
        container.add_widget(input_field)
        return container

    def _add_login_button(self, container):
        login_button = RoundedButton(
            text="Login",
            pos_hint={'center_x': 0.5}
        )
        login_button.bind(on_press=self.verify_credentials)
        container.add_widget(login_button)

    def _finalize_layout(self, center_container):
        self.main_layout.add_widget(Widget())
        self.main_layout.add_widget(center_container)
        self.main_layout.add_widget(Widget())
        self.add_widget(self.main_layout)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def show_error_popup(self, message):
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(None, None),
            size=(300, 150)
        )
        popup.open()

    def on_username_enter(self, instance):
        self.password_input.focus = True

    def verify_credentials(self, instance=None):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()

        if not username or not password:
            self.show_error_popup("Please enter both username and password")
            return

        if username == "user" and password == "password":
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = "main_screen"
        else:
            self.show_error_popup("Invalid username or password")
            self.password_input.text = ""

    def logout(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = "login_screen"

class SobotifyApp(App):
    def build(self):
        self.title = 'Sobotify'
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login_screen"))
        sm.add_widget(MainScreen(name="main_screen"))
        return sm

if __name__ == "__main__":
    SobotifyApp().run()
