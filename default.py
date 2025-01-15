from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.properties import ObjectProperty

# Set initial window size
Window.size = (400, 600)

class CustomTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.95, 0.95, 0.95, 1)  # Light gray background
        self.foreground_color = (0.2, 0.2, 0.2, 1)     # Dark text
        self.cursor_color = (0.2, 0.2, 0.2, 1)         # Dark cursor
        self.padding = [10, 10]                         # Add padding
        self.size_hint = (None, None)
        self.width = 300
        self.height = 40

class CustomButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.2, 0.6, 1, 1)       # Blue button
        self.size_hint = (None, None)
        self.width = 300
        self.height = 50
        
    def on_press(self):
        self.background_color = (0.1, 0.5, 0.9, 1)     # Darker blue when pressed
        
    def on_release(self):
        self.background_color = (0.2, 0.6, 1, 1)       # Return to original color

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Main layout
        self.layout = BoxLayout(orientation='vertical', spacing=20, padding=30)
        
        # App title
        self.title = Label(
            text="Welcome",
            font_size='24sp',
            size_hint_y=None,
            height=100
        )
        
        # Username input
        self.username_label = Label(
            text="Username",
            size_hint_y=None,
            height=30,
            halign='left'
        )
        self.username_input = CustomTextInput(
            multiline=False,
            hint_text='Enter username'
        )
        
        # Password input
        self.password_label = Label(
            text="Password",
            size_hint_y=None,
            height=30,
            halign='left'
        )
        self.password_input = CustomTextInput(
            password=True,
            multiline=False,
            hint_text='Enter password'
        )
        
        # Login button
        self.login_button = CustomButton(
            text="Login",
            on_press=self.login
        )
        
        # Add all widgets
        widgets = [
            self.title,
            self.username_label,
            self.username_input,
            self.password_label,
            self.password_input,
            self.login_button
        ]
        
        for widget in widgets:
            self.layout.add_widget(widget)
        
        self.add_widget(self.layout)
    
    def show_error_popup(self, message):
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(None, None),
            size=(300, 150)
        )
        popup.open()
    
    def login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if not username or not password:
            self.show_error_popup("Please enter both username and password")
            return
        
        # Replace with actual authentication logic
        if username == "user" and password == "password":
            # Add transition animation
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = "main_screen"
        else:
            self.show_error_popup("Invalid username or password")
            self.password_input.text = ""  # Clear password field

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.layout = BoxLayout(orientation='vertical', spacing=20, padding=30)
        
        # Welcome message
        self.welcome_label = Label(
            text="Welcome to the App!",
            font_size='24sp'
        )
        
        # Logout button
        self.logout_button = CustomButton(
            text="Logout",
            on_press=self.logout
        )
        
        self.layout.add_widget(self.welcome_label)
        self.layout.add_widget(self.logout_button)
        
        self.add_widget(self.layout)
    
    def logout(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = "login_screen"

class SobotifyApp(App):
    def build(self):
        # Set app theme colors
        self.title = 'Sobotify'
        
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login_screen"))
        sm.add_widget(MainScreen(name="main_screen"))
        return sm

if __name__ == "__main__":
    SobotifyApp().run()