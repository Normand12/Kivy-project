from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from functools import partial
import os
import sys
import subprocess
import psutil
import threading


# Defaults and Constants
DEFAULT_ROBOT_IP = "192.168.0.141"
DEFAULT_ROBOT_NAMES = ["stickman", "pepper", "nao", "cozmo", "mykeepon"]
DEFAULT_LANGUAGES = ["german", "english"]


def find_conda():
    if sys.platform.startswith('win'):
        conda_executable = 'conda.bat'
    else:
        conda_executable = 'conda'

    possible_paths = [
        os.path.join(os.path.expanduser("~"), "miniconda3", "condabin", conda_executable),
        os.path.join(os.path.expanduser("~"), "anaconda3", "condabin", conda_executable),
        os.path.join(os.path.expanduser("~"), "AppData", "Local", "miniconda3", "condabin", conda_executable),
        os.path.join(os.path.expanduser("~"), "AppData", "Local", "Continuum", "anaconda3", "condabin", conda_executable),
    ]

    for path in possible_paths:
        if os.path.isfile(path):
            return path

    # If conda is in PATH, return just the executable name
    if os.system(f"which {conda_executable} > /dev/null 2>&1") == 0:
        return conda_executable

    print("Cannot find Conda executable path. Abort")
    sys.exit(1)

conda_exe = find_conda()

def get_gestures():
    gestures = []
    assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
    if os.path.exists(assets_path):
        gesture_files = os.listdir(assets_path)
        for gesture in gesture_files:
            gesture_name, ext = os.path.splitext(gesture)
            if ext in [".xlsx"]:
                gestures.append(gesture_name)
    return gestures

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = kwargs.get('bg_color', (0.2, 0.6, 1, 1))
        self.size_hint = (None, None)
        self.width = kwargs.get('width', dp(120))
        self.height = kwargs.get('height', dp(40))
        with self.canvas.before:
            Color(*self.background_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class RoundedSpinner(Spinner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0.95, 0.95, 0.95, 1)
        self.size_hint = (None, None)
        self.width = dp(200)
        self.height = dp(40)
        with self.canvas.before:
            Color(*self.background_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class RoundedTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.size_hint = (None, None)
        self.width = dp(200)
        self.height = dp(40)
        self.multiline = False
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.clearcolor = (0.9, 0.9, 0.9, 1)  # Light gray background
        
        self.gesture_proc = None
        self.extract_proc = None
        self.current_gesture_index = 0
        
        self.robot_IP = DEFAULT_ROBOT_IP
        self.selected_robot = DEFAULT_ROBOT_NAMES[0]
        self.selected_language = DEFAULT_LANGUAGES[0]
        self.gestures = get_gestures()
        self.selected_curr_gesture = self.gestures[0] if self.gestures else ""
        
        self.build_ui()

    def build_ui(self):
        # Main layout
        main_layout = BoxLayout(orientation='vertical')

        # Top section with settings and logout
        top_section = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(150))
        
        # Settings container (left side)
        settings_container = BoxLayout(orientation='vertical', spacing=10, padding=[dp(25), dp(20), 0, 0])
        
        # Robot settings
        settings_container.add_widget(Label(text="Robot Name", size_hint=(None, None), height=dp(20)))
        self.robot_spinner = RoundedSpinner(text=self.selected_robot, values=DEFAULT_ROBOT_NAMES)
        settings_container.add_widget(self.robot_spinner)
        
        # IP settings
        settings_container.add_widget(Label(text="Robot IP", size_hint=(None, None), height=dp(20)))
        self.robot_ip_input = RoundedTextInput(text=self.robot_IP)
        settings_container.add_widget(self.robot_ip_input)
        
        # Language settings
        settings_container.add_widget(Label(text="Language", size_hint=(None, None), height=dp(20)))
        self.language_spinner = RoundedSpinner(text=self.selected_language, values=DEFAULT_LANGUAGES)
        settings_container.add_widget(self.language_spinner)
        
        top_section.add_widget(settings_container)
        
        # Logout button (right side)
        logout_container = BoxLayout(padding=[0, dp(20), dp(25), 0])
        logout_button = RoundedButton(
            text="Logout",
            width=dp(100),
            bg_color=(0.7, 0.3, 0.3, 1)
        )
        logout_button.bind(on_press=self.logout)
        logout_container.add_widget(logout_button)
        top_section.add_widget(logout_container)
        
        main_layout.add_widget(top_section)

        # Gesture section (bottom half)
        gesture_section = BoxLayout(orientation='vertical', spacing=20, padding=[0, dp(20), 0, dp(20)])
        
        # Gesture slider
        slider_container = BoxLayout(orientation='horizontal', size_hint_x=0.5, pos_hint={'center_x': 0.5})
        
        left_arrow = RoundedButton(
            text="←",
            width=dp(50),
            bg_color=(0.4, 0.4, 0.4, 1),
            on_press=partial(self.change_gesture, -1)
        )
        
        self.gesture_label = Label(
            text=self.selected_curr_gesture,
            size_hint_x=None,
            width=dp(200)
        )
        
        right_arrow = RoundedButton(
            text="→",
            width=dp(50),
            bg_color=(0.4, 0.4, 0.4, 1),
            on_press=partial(self.change_gesture, 1)
        )
        
        slider_container.add_widget(left_arrow)
        slider_container.add_widget(self.gesture_label)
        slider_container.add_widget(right_arrow)
        
        gesture_section.add_widget(slider_container)
        
        # Control buttons
        control_container = BoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            width=dp(300),
            height=dp(50),
            spacing=20,
            pos_hint={'center_x': 0.5}
        )
        
        start_button = RoundedButton(
            text="Start",
            bg_color=(0.2, 0.7, 0.2, 1),
            on_press=self.start_gesture
        )
        
        stop_button = RoundedButton(
            text="Stop",
            bg_color=(0.7, 0.2, 0.2, 1),
            on_press=self.stop_gesture
        )
        
        control_container.add_widget(start_button)
        control_container.add_widget(stop_button)
        
        gesture_section.add_widget(control_container)
        main_layout.add_widget(gesture_section)
        
        self.add_widget(main_layout)

    def change_gesture(self, direction, instance):
        if self.gestures:
            self.current_gesture_index = (self.current_gesture_index + direction) % len(self.gestures)
            self.selected_curr_gesture = self.gestures[self.current_gesture_index]
            self.gesture_label.text = self.selected_curr_gesture

    def start_gesture(self, *args):
        def run_gesture():
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools', 'robotcontrol', 'robotcontrol.py')
            conda_env = "sobotify_naoqi" if self.robot_spinner.text.lower() in ["pepper", "nao"] else "sobotify"

            arguments = [
                conda_exe, "run", "-n", conda_env, "--no-capture-output", "python", script_path,
                "--robot_name", self.robot_spinner.text,
                "--robot_ip", self.robot_ip_input.text,
                "--language", self.language_spinner.text,
                "--gesture", self.selected_curr_gesture
            ]

            print("Running command:", " ".join(arguments))
            self.gesture_proc = subprocess.Popen(arguments, creationflags=subprocess.CREATE_NEW_CONSOLE)

        threading.Thread(target=run_gesture, daemon=True).start()

    def stop_gesture(self, *args):
        def stop_process():
            if self.gesture_proc:
                try:
                    if psutil.pid_exists(self.gesture_proc.pid):
                        process = psutil.Process(self.gesture_proc.pid)
                        for child in process.children(recursive=True):
                            child.kill()
                        process.kill()
                    else:
                        print(f"Process {self.gesture_proc.pid} not found.")
                except psutil.NoSuchProcess:
                    print("Process does not exist.")
                self.gesture_proc = None

        threading.Thread(target=stop_process, daemon=True).start()

    def logout(self, instance):
        self.manager.transition.direction = 'right'
        self.manager.current = 'login_screen'