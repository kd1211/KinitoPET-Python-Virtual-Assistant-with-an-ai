import os
import sys
import tkinter as tk
from tkinter import Toplevel, messagebox
import pyttsx3
from PIL import Image, ImageTk
import threading
import random
import time
import math
import pyautogui
import subprocess
# pygame removed from top-level imports to allow running without installing it
from datetime import datetime

# Helper to support PyInstaller onefile bundles
def resource_path(rel_path):
    """Return absolute path to resource, works for dev and for PyInstaller bundle."""
    base = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
    return os.path.join(base, rel_path)

# Get the script's directory and asset paths
script_directory = os.path.dirname(os.path.realpath(__file__))
assets_directory = resource_path(os.path.join("GameAssets"))
programs_directory = os.path.join(assets_directory, "Programs")
balconexe_directory = os.path.join(programs_directory, "balcon.exe")

sprite_path_normal = os.path.join(assets_directory, "KinitoNormal.png")
sprite_path_normal_2 = os.path.join(assets_directory, "KinitoNormal2.png")
sprite_path_moving = os.path.join(assets_directory, "Kinito.png")
sprite_path_sleep = os.path.join(assets_directory, "Sleep.png")
sprite_path_sleep1 = os.path.join(assets_directory, "Sleep1.png")
sprite_path_sleep2 = os.path.join(assets_directory, "Sleep2.png")
sprite_path_sleep3 = os.path.join(assets_directory, "Sleep3.png")
sprite_path_thinking = os.path.join(assets_directory, "Thinking.png")
sprite_path_thinking2 = os.path.join(assets_directory, "Thinking2.png")

newbeginnings_file_path = os.path.join(assets_directory, "NewBeginningsPoemEdit.mp3")
timer_file_path = os.path.join(assets_directory, "Timer.mp3")
tune_file_path = os.path.join(assets_directory, "TinyTune.mp3")
starttalk_file_path = os.path.join(assets_directory, "StartTalking.mp3")
stoptalk_file_path = os.path.join(assets_directory, "StopTalking.mp3")
woosh_file_path = os.path.join(assets_directory, "Woosh.mp3")
surf_file_path = os.path.join(assets_directory, "Surf.mp3")
bomp_file_path = os.path.join(assets_directory, "Bomp.mp3")

# Initialize Text-to-Speech engine
engine = pyttsx3.init()

# Simple helper: speak via pyttsx3 as a fallback
def fallback_speak(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass

class FloatingAssistant:
    def __init__(self, root, image_path):
        self.root = root
        self.root.overrideredirect(True)  # Remove window decorations
        try:
            self.root.attributes('-transparentcolor', 'white')  # Set transparent color
        except Exception:
            pass

        # Load images from the GameAssets folder (fail fast if missing)
        self.img_normal = Image.open(sprite_path_normal)
        self.img_normal_2 = Image.open(sprite_path_normal_2)
        self.img_moving = Image.open(image_path)
        self.img_sleep = Image.open(sprite_path_sleep)
        self.img_sleep1 = Image.open(sprite_path_sleep1)
        self.img_sleep2 = Image.open(sprite_path_sleep2)
        self.img_sleep3 = Image.open(sprite_path_sleep3)
        self.img_thinking = Image.open(sprite_path_thinking)
        self.img_thinking2 = Image.open(sprite_path_thinking2)

        self.tk_img_normal = ImageTk.PhotoImage(self.img_normal)
        self.tk_img_normal_2 = ImageTk.PhotoImage(self.img_normal_2)
        self.tk_img_moving = ImageTk.PhotoImage(self.img_moving)
        self.tk_img_sleep = ImageTk.PhotoImage(self.img_sleep)
        self.tk_img_sleep3 = ImageTk.PhotoImage(self.img_sleep3)
        self.tk_img_sleep2 = ImageTk.PhotoImage(self.img_sleep2)
        self.tk_img_sleep1 = ImageTk.PhotoImage(self.img_sleep1)
        self.tk_img_thinking = ImageTk.PhotoImage(self.img_thinking)
        self.tk_img_thinking2 = ImageTk.PhotoImage(self.img_thinking2)
        
        # Display image
        self.panel = tk.Label(self.root, bg='white')
        self.panel.pack(side="top", fill="both", expand=True)
        self.change_sprite(self.tk_img_normal)

        # Make the window float
        self.x = random.randint(100, 500)
        self.y = random.randint(100, 500)
        self.root.geometry(f"+{self.x}+{self.y}")
        self.paused = False
        self.talking = False
        self.normalclosebubble = True
        try:
            self.root.wm_attributes("-topmost", True)
        except Exception:
            pass

        # Start background threads
        threading.Thread(target=self.smooth_movement, daemon=True).start()
        threading.Thread(target=self.idle_animation, daemon=True).start()
        threading.Thread(target=self.update_speech_bubble_position, daemon=True).start()

        # Bind controls
        self.root.bind("<Button-3>", self.ask_waht_todo)
        self.root.bind('<Double-Button-1>', lambda e: self.show_ai_chat_window())

        self.is_dragging = False
        self.mouse_click_offset_x = 0
        self.mouse_click_offset_y = 0
        self.setup_mouse_bindings()

        # track current question separately so handle_response can work even if bubble was destroyed
        self.current_question = ""

    def ask_waht_todo(self, event=None):
        self.speak("What would you like me to do?", 45, True)

    def setup_mouse_bindings(self):
        self.root.bind('<Button-1>', self.on_mouse_down)
        self.root.bind('<B1-Motion>', self.on_mouse_move)
        self.root.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.x, self.y = self.root.winfo_x(), self.root.winfo_y()

    def on_mouse_down(self, event):
        self.is_dragging = True
        self.play_mp3(woosh_file_path)
        self.root.update_idletasks()
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        self.mouse_click_offset_x = root_x - event.x_root
        self.mouse_click_offset_y = root_y - event.y_root

    def on_mouse_move(self, event):
        if self.is_dragging:
            new_x = event.x_root + self.mouse_click_offset_x
            new_y = event.y_root + self.mouse_click_offset_y
            self.root.geometry(f"+{int(new_x)}+{int(new_y)}")

    def on_mouse_up(self, event):
        self.is_dragging = False
        self.play_mp3(bomp_file_path)

    def toggle_pause(self):
        if self.paused:
            self.unpause()
        else:
            self.pause()

    def pause(self):
        self.speak("I'm taking a nap! Wake me up if you need me!")
        self.paused = True

    def unpause(self):
        self.paused = False
        self.change_sprite(self.tk_img_normal)
        self.speak("I have woken up! What do you need?")
        threading.Thread(target=self.smooth_movement, daemon=True).start()
        threading.Thread(target=self.idle_animation, daemon=True).start()
        threading.Thread(target=self.update_speech_bubble_position, daemon=True).start()

    def speak(self, text, pitch=45, slow=False):
        command = [balconexe_directory, "-n", "Eddie", "-t", text, "-p", str(pitch)]
        self.talking = True
        try:
            subprocess.run(command, check=True)
        except Exception:
            fallback_speak(text)

        if slow:
            self.root.after(0, lambda: self.show_speech_bubble(text, False))
        else:
            self.root.after(0, lambda: self.show_speech_bubble(text))

    def speak_whisper(self, text, pitch=45, slow=False):
        command = [balconexe_directory, "-n", "Female Whisper", "-t", text, "-p", str(pitch)]
        self.talking = True
        try:
            subprocess.run(command, check=True)
        except Exception:
            fallback_speak(text)

        if slow:
            self.root.after(0, lambda: self.show_speech_bubble(text, False))
        else:
            self.root.after(0, lambda: self.show_speech_bubble(text))

    def show_speech_bubble(self, text, evergoaway=True):
        # Close existing bubble if present
        if hasattr(self, 'speech_bubble') and self.speech_bubble.winfo_exists():
            self.close_speech_bubble()

        self.current_question = text
        self.play_mp3(starttalk_file_path)
        self.speech_bubble = Toplevel(self.root)
        self.speech_bubble.overrideredirect(True)
        try:
            self.speech_bubble.attributes('-transparentcolor', 'white')
        except Exception:
            pass

        self.speech_bubble.wm_title(text)
        label = tk.Label(self.speech_bubble, text=text, bg='light gray', fg='black')
        label.pack(ipadx=5, ipady=5)

        # Provide some quick-response buttons depending on prompt
        if "What would you like me to do?" in text:
            self.show_response_buttons(["Set a Reminder", "Tell Me the Time", "Toggle Sleep", "Sing a Song", "Tell Me a Fun Fact", "Simon Says", "Ask AI"])
        elif "How is your day?" in text:
            self.show_response_buttons(["Good", "Bad"])

        if evergoaway:
            # schedule to close the bubble after 5 seconds
            self.root.after(5000, self.close_speech_bubble)

    def show_response_buttons(self, options):
        if hasattr(self, 'speech_bubble') and self.speech_bubble.winfo_exists():
            button_frame = tk.Frame(self.speech_bubble, bg='white')
            button_frame.pack()
            for option in options:
                # use a small wrapper to avoid late binding issues
                def make_cmd(resp):
                    return lambda: self.handle_response(resp)
                option_button = tk.Button(button_frame, text=option, command=make_cmd(option))
                option_button.pack(side=tk.LEFT, padx=5)

    def show_response_textbox(self, prompt):
        if hasattr(self, 'speech_bubble') and self.speech_bubble.winfo_exists():
            entry = tk.Entry(self.speech_bubble, bg='light gray', fg='black')
            entry.pack(ipadx=10, ipady=5)
            entry.bind('<Return>', lambda event: self.handle_response(entry.get()))
        else:
            self.speech_bubble = Toplevel(self.root)
            self.speech_bubble.overrideredirect(True)
            try:
                self.speech_bubble.attributes('-transparentcolor', 'white')
            except Exception:
                pass
            self.speech_bubble.wm_title(prompt)
            label = tk.Label(self.speech_bubble, text=prompt, bg='light gray', fg='black')
            label.pack(ipadx=10, ipady=5)
            entry = tk.Entry(self.speech_bubble, bg='light gray', fg='black')
            entry.pack(ipadx=10, ipady=5)
            entry.bind('<Return>', lambda event: self.handle_response(entry.get()))

    def handle_response(self, response):
        # Safely determine the current question
        if hasattr(self, 'speech_bubble') and getattr(self, 'speech_bubble') is not None:
            try:
                if self.speech_bubble.winfo_exists():
                    current_question = self.speech_bubble.wm_title()
                else:
                    current_question = self.current_question
            except Exception:
                current_question = self.current_question
        else:
            current_question = self.current_question

        # Handle the user's response here
        if "What would you like me to do?" in current_question:
            if response == "Set a Reminder":
                self.speak("How many minutes until I should remind you?", 45, True)
            elif response == "Toggle Sleep":
                self.toggle_pause()
            elif response == "Sing a Song":
                self.say_random_poem()
            elif response == "Tell Me a Fun Fact":
                self.say_random_fact()
            elif response == "Simon Says":
                self.speak("Sure! What would you like me to say?", 45, True)
            elif response == "Tell Me the Time":
                self.print_current_datetime()
            elif response == "Ask AI":
                self.show_ai_chat_window()
        elif "How many minutes until I should remind you?" in current_question:
            self.set_reminder(f"{response}")
        elif "Sure! What would you like me to say?" in current_question:
            self.speak(f"{response}")
        elif "How is your day?" in current_question:
            if response == "Good":
                self.speak("That's great, having a friend around is always a good time!")
            elif response == "Bad":
                self.speak("Thats too bad, I hope I can cheer you up!")
        # Close the bubble after handling the response
        self.close_speech_bubble()

    def close_speech_bubble(self):
        if hasattr(self, 'speech_bubble') and self.speech_bubble is not None:
            try:
                if self.speech_bubble.winfo_exists():
                    self.speech_bubble.destroy()
            except Exception:
                pass
        # keep the current_question string for potential handling
        self.play_mp3(stoptalk_file_path)
        self.talking = False

    def update_speech_bubble_position(self):
        while True:
            if hasattr(self, 'speech_bubble') and getattr(self, 'speech_bubble') is not None:
                try:
                    if self.speech_bubble.winfo_exists():
                        bubble_x = self.root.winfo_x() + 50
                        bubble_y = self.root.winfo_y() - 30
                        self.speech_bubble.geometry(f"+{bubble_x}+{bubble_y}")
                    else:
                        # If the bubble was destroyed, set to None but keep current_question
                        try:
                            del self.speech_bubble
                        except Exception:
                            self.speech_bubble = None
                except Exception:
                    pass
            time.sleep(0.1)

    def play_random_program(self):
        # Try to get the desktop path for the current user
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        try:
            if os.path.exists(desktop_path) and os.path.isdir(desktop_path):
                desktop_contents = os.listdir(desktop_path)
                shortcut_files = [f for f in desktop_contents if f.lower().endswith('.lnk')]
                if shortcut_files:
                    selected_shortcut = random.choice(shortcut_files)
                    os.startfile(os.path.join(desktop_path, selected_shortcut))
                else:
                    self.speak("It seems there are no shortcuts on your desktop. Let's try something else.")
                    self.speak_random_question()
            else:
                onedrive_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
                if os.path.exists(onedrive_path) and os.path.isdir(onedrive_path):
                    onedrive_contents = os.listdir(onedrive_path)
                    onedrive_shortcuts = [f for f in onedrive_contents if f.lower().endswith('.lnk')]
                    if onedrive_shortcuts:
                        selected_shortcut = random.choice(onedrive_shortcuts)
                        os.startfile(os.path.join(onedrive_path, selected_shortcut))
                    else:
                        self.speak("It seems there are no shortcuts in your OneDrive Desktop. Let's try something else.")
                        self.speak_random_question()
                else:
                    self.speak("I couldn't find your desktop. Let's try something else.")
                    self.speak_random_question()
        except Exception:
            self.speak("I couldn't access your desktop. Let's try something else.")
            self.speak_random_question()

    def minimize_current_window(self):
        pyautogui.hotkey('winleft', 'down')

    def show_image(self):
        secret_images_folder = os.path.join(assets_directory, "SecretImages")
        if os.path.exists(secret_images_folder) and os.path.isdir(secret_images_folder):
            image_files = [file for file in os.listdir(secret_images_folder) if file.lower().endswith((".jpg", ".jpeg", ".png"))]
            if image_files:
                selected_image = random.choice(image_files)
                image_path = os.path.join(secret_images_folder, selected_image)
                self.show_image_window(image_path)
            else:
                self.speak("It seems there are no secret images to show you. Let's try something else.")
                self.speak_random_question()
        else:
            self.speak("I couldn't find the secret images folder. Let's try something else.")
            self.speak_random_question()

    def show_image_window(self, image_path):
        image_window = Toplevel(self.root)
        image_window.title("Image.png From: KinitoPET")
        image_window.geometry("800x600")
        img = Image.open(image_path)
        tk_img = ImageTk.PhotoImage(img)
        label = tk.Label(image_window, image=tk_img)
        label.image = tk_img
        label.pack(fill="both", expand=True)
        screen_width = image_window.winfo_screenwidth()
        screen_height = image_window.winfo_screenheight()
        x = (screen_width - 800) // 2
        y = (screen_height - 600) // 2
        image_window.geometry(f"800x600+{x}+{y}")
        image_window.wait_window(image_window)
        self.unfreeze_mouse()

    def freeze_mouse(self):
        self.root.bind("<Motion>", lambda event: "break")

    def unfreeze_mouse(self):
        self.root.unbind("<Motion>")

    def speak_random_question(self):
        questions = [
            "How is your day?",
            "What's your favorite color?",
            "Do you like programming?",
            "What is your favorite food?",
            "Is there a specific hobby you enjoy?",
            "How about we play a game!",
            "Hey! do you want to hear a poem I made just for you?",
            "Let me show you this cool image I have generated for you!",
            "Wanna hear a fun fact!?"
        ]
        question = random.choice(questions)
        if "What's your favorite color?" in question or "What is your favorite food?" in question or "Is there a specific hobby" in question:
            self.speak(question, 45, True)
        else:
            self.speak(question)

    def say_random_poem(self):
        poems = [
            "Roses are red, violets are blue, your virtual friend is here for you.",
            "Digital winds whisper in code, bringing helpfulness down every road.",
            "Tiny tunes hum, reminders ring, Kinito will help you do your thing."
        ]
        poem = random.choice(poems)
        self.play_mp3(newbeginnings_file_path)
        self.speak(poem)

    def say_random_fact(self):
        facts = [
            "Bananas are botanically berries.",
            "Honey can last for thousands of years.",
            "Octopuses have three hearts."
        ]
        fact = random.choice(facts)
        self.speak(fact)

    def smooth_movement(self):
        while True:
            if not self.paused:
                if random.random() < 0.5 and not self.talking:
                    self.speak_random_question()
                    time.sleep(random.randint(6, 15))
                else:
                    target_x = random.randint(100, 800)
                    target_y = random.randint(100, 800)
                    self.moving = True
                    self.change_sprite(self.tk_img_moving)
                    self.play_mp3(surf_file_path)
                    self.move_towards(target_x, target_y, speed=5)
                    self.moving = False
                    self.change_sprite(self.tk_img_normal)
                    time.sleep(random.randint(6, 15))
            else:
                time.sleep(0.5)

    def move_towards(self, target_x, target_y, speed):
        while True:
            if not self.paused:
                current_x, current_y = self.root.winfo_x(), self.root.winfo_y()
                if current_x == target_x and current_y == target_y:
                    break
                dx = target_x - current_x
                dy = target_y - current_y
                distance = math.hypot(dx, dy)
                self.change_sprite(self.tk_img_moving)
                steps = min(speed, distance)
                theta = math.atan2(dy, dx)
                self.x = current_x + steps * math.cos(theta)
                self.y = current_y + steps * math.sin(theta)
                self.root.geometry(f"+{int(self.x)}+{int(self.y)}")
                self.root.update()
                time.sleep(0.015)
            else:
                break

    def idle_animation(self):
        while True:
            if not self.paused and not self.talking:
                self.change_sprite(self.tk_img_normal)
                time.sleep(1)
                self.change_sprite(self.tk_img_normal_2)
                time.sleep(1)
            elif self.paused and not self.talking:
                self.change_sprite(self.tk_img_sleep)
                time.sleep(1)
                self.change_sprite(self.tk_img_sleep1)
                time.sleep(1)
                self.change_sprite(self.tk_img_sleep2)
                time.sleep(1)
                self.change_sprite(self.tk_img_sleep3)
                time.sleep(1)
            elif self.talking:
                self.change_sprite(self.tk_img_thinking)
                time.sleep(1)
                self.change_sprite(self.tk_img_thinking2)
                time.sleep(1)

    def set_reminder(self, minutes):
        digits = [char for char in str(minutes) if char.isdigit()]
        if digits:
            self.speak("Your reminder is set!")
            time.sleep(int(''.join(digits)) * 60)
            self.play_mp3(timer_file_path)
            self.speak("Hello! Your timer is done!")
        else:
            self.speak("Uh oh, it seems you didn't type any numbers! Try again.")

    def print_current_datetime(self):
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%H:%M")
        self.speak(f"The time is {formatted_datetime}!")

    def change_sprite(self, new_sprite):
        try:
            self.panel.config(image=new_sprite)
        except Exception:
            pass

    def play_mp3(self, file_path):
        # Try pygame if available, otherwise try playsound, then try Windows Media Player, then OS default
        # 1) pygame (if installed)
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            return
        except Exception:
            pass

        # 2) playsound (if installed)
        try:
            from playsound import playsound
            # play in background thread so it doesn't block the UI
            threading.Thread(target=lambda: playsound(file_path), daemon=True).start()
            return
        except Exception:
            pass

        # 3) On Windows try to use Windows Media Player directly to avoid opening VLC as default
        if sys.platform.startswith("win"):
            # Common path for Windows Media Player
            program_files = os.environ.get('ProgramFiles', r"C:\Program Files")
            wmplayer_path = os.path.join(program_files, "Windows Media Player", "wmplayer.exe")
            try:
                if os.path.exists(wmplayer_path):
                    # Start minimized using cmd start /min
                    subprocess.Popen(["cmd", "/c", "start", "/min", "", wmplayer_path, file_path])
                    return
            except Exception:
                pass

        # 4) Last resort: open with system default application (may open VLC if it's the default)
        try:
            if sys.platform.startswith("win"):
                os.startfile(file_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", file_path])
            else:
                subprocess.Popen(["xdg-open", file_path])
            return
        except Exception:
            try:
                fallback_speak("Unable to play audio file.")
            except Exception:
                pass

    # Minimal AI chat window (local echo AI). Replace with Ollama/OpenAI integration if desired.
    def show_ai_chat_window(self):
        win = Toplevel(self.root)
        win.title("Ask Kinito (AI)")
        win.geometry("400x200")
        tk.Label(win, text="Ask me anything:").pack(pady=6)
        entry = tk.Entry(win, width=60)
        entry.pack(pady=6)
        result = tk.Text(win, height=6, width=48)
        result.pack(pady=6)

        def submit():
            prompt = entry.get().strip()
            if not prompt:
                return
            # Simple local "AI" that echoes and adds a friendly reply.
            reply = f"You asked: {prompt}\nI'm still learning — here's a helpful tip: try to be specific about what you want."
            result.delete('1.0', tk.END)
            result.insert(tk.END, reply)
            self.speak(reply)

        tk.Button(win, text="Send", command=submit).pack(pady=4)


def main():
    root = tk.Tk()
    app = FloatingAssistant(root, sprite_path_moving)
    root.mainloop()

if __name__ == "__main__":
    main()
