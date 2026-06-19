import os
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
import pygame
from datetime import datetime
import requests

# Get the script's directory
script_directory = os.path.dirname(os.path.realpath(__file__))
assets_directory = os.path.join(script_directory, "GameAssets")
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

# Simple helper: speak via pyttsx3 as a fallback (not used by default, the project uses balcon.exe)
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
        self.root.attributes('-transparentcolor', 'white')  # Set transparent color

        # Load images from the GameAssets folder
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
        self.panel.pack(side="top", fill="both", expand="yes")
        self.change_sprite(self.tk_img_normal)

        # Make the window float
        self.x = random.randint(100, 500)
        self.y = random.randint(100, 500)
        self.root.geometry(f"+{self.x}+{self.y}")
        self.paused = False
        self.talking = False
        self.normalclosebubble = True
        # Set the window to stay on top of all other windows
        self.root.wm_attributes("-topmost", True)

        # Start the smooth movement
        threading.Thread(target=self.smooth_movement, daemon=True).start()

        # Start the idle animation
        threading.Thread(target=self.idle_animation, daemon=True).start()

        # Start the speech bubble position update thread
        threading.Thread(target=self.update_speech_bubble_position, daemon=True).start()

        # Bind right-click to pause/unpause
        self.root.bind("<Button-3>", self.ask_waht_todo)
        
        self.is_dragging = False
        self.mouse_click_offset_x = 0
        self.mouse_click_offset_y = 0
        # Ensure your initialization includes setting up the mouse event bindings
        self.setup_mouse_bindings()

        # Bind double-click to open AI chat window
        self.root.bind('<Double-Button-1>', lambda e: self.show_ai_chat_window())

    def ask_waht_todo(self, event=None):
        # Open main question (added an Ask AI option)
        self.speak("What would you like me to do?", 45, True)

    def setup_mouse_bindings(self):
        # This method needs to be connected to the actual GUI event handling system you're using.
        # For example, in Tkinter you would bind mouse events to the window or canvas.
        self.root.bind('<Button-1>', self.on_mouse_down)  # Left mouse button down
        self.root.bind('<B1-Motion>', self.on_mouse_move)  # Left mouse button held and moved
        self.root.bind('<ButtonRelease-1>', self.on_mouse_up)  # Left mouse button release
        self.x, self.y = self.root.winfo_x(), self.root.winfo_y()

    def on_mouse_down(self, event):
        self.is_dragging = True
        self.play_mp3(woosh_file_path)
        # Get the root window's current position
        self.root.update_idletasks()  # Ensure window position is up-to-date
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        # Calculate the offset from the window's top-left corner to the mouse
        self.mouse_click_offset_x = root_x - event.x_root
        self.mouse_click_offset_y = root_y - event.y_root

    def on_mouse_move(self, event):
        if self.is_dragging:
            # Calculate the new position based on the mouse's position and the initial offsets
            new_x = event.x_root + self.mouse_click_offset_x
            new_y = event.y_root + self.mouse_click_offset_y
            # Update the window position
            self.root.geometry(f"+{int(new_x)}+{int(new_y)}")

    def on_mouse_up(self, event):
        # Called when the left mouse button is released
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
        # Ensure the path to balcon.exe is correct and escape any spaces in paths
        command = [balconexe_directory, "-n", "Eddie", "-t", text, "-p", str(pitch)]
        self.talking = True;
        # Execute the command
        try:
            subprocess.run(command, check=True)
        except Exception:
            # If balcon isn't available, fallback to pyttsx3 (if installed/configured)
            fallback_speak(text)

        if slow == True:
            self.root.after(0, lambda: self.show_speech_bubble(text, False))
        else:
            self.root.after(0, lambda: self.show_speech_bubble(text))

    def speak_whisper(self, text, pitch=45, slow=False):
        # Ensure the path to balcon.exe is correct and escape any spaces in paths
        command = [balconexe_directory, "-n", "Female Whisper", "-t", text, "-p", str(pitch)]
        self.talking = True;
        # Execute the command
        try:
            subprocess.run(command, check=True)
        except Exception:
            fallback_speak(text)

        if slow == True:
            self.root.after(0, lambda: self.show_speech_bubble(text, False))
        else:
            self.root.after(0, lambda: self.show_speech_bubble(text))

    def show_speech_bubble(self, text, evergoaway=True):
        # Check if a speech bubble is already present and close it
        if hasattr(self, 'speech_bubble') and self.speech_bubble.winfo_exists():
            self.close_speech_bubble()
            
        self.play_mp3(starttalk_file_path)
        self.speech_bubble = Toplevel(self.root)
        self.speech_bubble.overrideredirect(True)
        self.speech_bubble.attributes('-transparentcolor', 'white')

        # Set the title of the speech bubble to identify the current question
        self.speech_bubble.wm_title(text)

        # Adjust the vertical position of the speech bubble
        label = tk.Label(self.speech_bubble, text=text, bg='light gray', fg='black')
        label.pack(ipadx=5, ipady=5)

        # Check if the question requires user response with buttons
        if "What would you like me to do?" in text:
            self.show_response_buttons(["Set a Reminder", "Tell Me the Time", "Toggle Sleep", "Sing a Song", "Tell Me a Fun Fact", "Simon Says", "Ask AI"])
        elif "How is your day?" in text:
            self.show_response_buttons(["Good", "Bad"])
        elif "What's your favorite color?" in text:
            self.show_response_textbox("What's your favorite color?")
        elif "Do you like programming?" in text:
            self.show_response_buttons(["Yes", "No"])
        elif "Is there a specific hobby you enjoy?" in text:
            self.show_response_textbox("Is there a specific hobby you enjoy?")
        elif "How about we play a game" in text:
            self.show_response_buttons(["Okay", "Not now"])
        elif "Let me show you this cool image I have generated for you!" in text:
            self.show_response_buttons(["Okay", "Not now"])
        elif "What is your favorite food?" in text:
            self.show_response_textbox("What is your favorite food?")
        elif "Hey! do you want to hear a poem I made just for you?" in text:
            self.show_response_buttons(["Yes", "No, Your poems suck."])
        elif "Wanna hear a fun fact!?" in text:
            self.show_response_buttons(["Sure", "Not now"])
        elif "How many minutes until I should remind you?" in text:
            self.show_response_textbox("How many minutes until I should remind you?")
        elif "Sure! What would you like me to say?" in text:
            self.show_response_textbox("Sure! What would you like me to say?")

        # Close the speech bubble after 5 seconds (adjust as needed)
        if evergoaway == True:
            self.root.after(5000, self.close_speech_bubble)

    def show_response_buttons(self, options):
        if hasattr(self, 'speech_bubble') and self.speech_bubble.winfo_exists():
            button_frame = tk.Frame(self.speech_bubble, bg='white')
            button_frame.pack()

            for option in options:
                option_button = tk.Button(button_frame, text=option, command=lambda response=option: self.handle_response(response))
                option_button.pack(side=tk.LEFT, padx=5)

    def show_response_textbox(self, prompt):
        if hasattr(self, 'speech_bubble') and self.speech_bubble.winfo_exists():
            # Add a text box below the existing speech bubble's label
            entry = tk.Entry(self.speech_bubble, bg='light gray', fg='black')
            entry.pack(ipadx=10, ipady=5)
            entry.bind('<Return>', lambda event: self.handle_response(entry.get()))
        else:
            # Create a new speech bubble with the prompt and a text box
            self.speech_bubble = Toplevel(self.root)
            self.speech_bubble.overrideredirect(True)
            self.speech_bubble.attributes('-transparentcolor', 'white')
            self.speech_bubble.wm_title(prompt)

            # Create a label for the prompt
            label = tk.Label(self.speech_bubble, text=prompt, bg='light gray', fg='black')
            label.pack(ipadx=10, ipady=5)

            # Create a text box for user input
            entry = tk.Entry(self.speech_bubble, bg='light gray', fg='black')
            entry.pack(ipadx=10, ipady=5)
            entry.bind('<Return>', lambda event: self.handle_response(entry.get()))

            # Close the speech bubble after a certain time (e.g., 30 seconds)
            #self.root.after(30000, self.close_speech_bubble)

    def handle_response(self, response):
        # Handle the user's response here
        current_question = self.speech_bubble.wm_title()
        
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
                # Open AI chat input window
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
        elif "What's your favorite color?" in current_question:
            self.speak(f"Nice choice! {response} is a wonderful color!")
        elif "Do you like programming?" in current_question:
            if response == "Yes":
                self.speak("Programming is amazing! if it weren't for programming, I wouldn't be here!")
            elif response == "No":
                self.speak("Thats a shame. I love ones and zeros.")
        elif "Is there a specific hobby you enjoy?" in current_question:
            self.speak(f"I can see how {response} is fun!")
        elif "Wanna hear a fun fact!?" in current_question:
            if response == "Sure":
                self.say_random_fact()
            elif response == "Not now":
                self.speak("Thats okay! Maybe later.")
        elif "How about we play a game" in current_question:
            if response == "Okay":
                self.play_random_program()
            elif response == "Not now":
                self.speak("Sure, we can do something else.")
        elif "Let me show you this cool image I have generated for you!" in current_question:
            if response == "Okay":
                self.show_image()
            elif response == "Not now":
                self.speak("I get it. You are to busy paying too much attention to something that's not important.", 20)
                self.minimize_current_window()
                self.minimize_current_window()
                self.minimize_current_window()
                self.minimize_current_window()
                self.minimize_current_window()
                self.minimize_current_window()
                self.minimize_current_window()
                self.minimize_current_window()
        elif "What is your favorite food?" in current_question:
            self.speak(f"I agree! {response} tastes amazing!")
        elif "Hey! do you want to hear a poem I made just for you?" in current_question:
            if response == "Yes":
                self.say_random_poem()
            elif response == "No, Your poems suck.":
                self.speak("That's a shame. I took a lot of time to make it. maybe you're just paying too much attention to what you're doing.", 20)
                self.minimize_current_window()
                self.minimize_current_window()
                self.minimize_current_window()
                self.minimize_current_window()
                self.minimize_current_window()
                self.minimize_current_window()
                self.minimize_current_window()
                self.minimize_current_window()
                
        # Close the speech bubble after handling the response
        self.close_speech_bubble()

    def close_speech_bubble(self):
        if hasattr(self, 'speech_bubble') and self.speech_bubble.winfo_exists():
            self.speech_bubble.destroy()
            self.play_mp3(stoptalk_file_path)
            self.talking = False

    def update_speech_bubble_position(self):
        while True:
            if hasattr(self, 'speech_bubble'):
                try:
                    if self.speech_bubble.winfo_exists():
                        # Position the speech bubble above the assistant
                        bubble_x = self.root.winfo_x() + 50
                        bubble_y = self.root.winfo_y() - 30
                        self.speech_bubble.geometry(f"+{bubble_x}+{bubble_y}")
                    else:
                        # Speech bubble closed, remove the attribute
                        delattr(self, 'speech_bubble')
                except tk.TclError:
                    # Handle the case where the speech_bubble is already destroyed
                    pass
            time.sleep(0.1)  # Adjust the sleep duration as needed

    def play_random_program(self):
        # Try to get the desktop path for the current user
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

        print(f"Desktop Path: {desktop_path}")

        try:
            # Check if the desktop path exists and is a directory
            if os.path.exists(desktop_path) and os.path.isdir(desktop_path):
                # Get a list of all files on the desktop
                desktop_contents = os.listdir(desktop_path)
                print(f"Desktop Contents: {desktop_contents}")

                # Get a list of shortcut files on the desktop
                shortcut_files = [file for file in desktop_contents if file.endswith(".lnk")]

                if shortcut_files:
                    # Choose a random shortcut
                    selected_shortcut = random.choice(shortcut_files)

                    # Open the selected shortcut without asking the user
                    os.startfile(os.path.join(desktop_path, selected_shortcut))
                
                else:
                    # No shortcut files found on the desktop
                    self.speak("It seems there are no shortcuts on your desktop. Let's try something else.")
                    self.speak_random_question()
            else:
                # Check if the OneDrive path exists and is a directory
                onedrive_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
                if os.path.exists(onedrive_path) and os.path.isdir(onedrive_path):
                    # Get a list of all files in the OneDrive Desktop folder
                    onedrive_contents = os.listdir(onedrive_path)
                    print(f"OneDrive Desktop Contents: {onedrive_contents}")

                    # Get a list of shortcut files in the OneDrive Desktop folder
                    onedrive_shortcuts = [file for file in onedrive_contents if file.endswith(".lnk")]

                    if onedrive_shortcuts:
                        # Choose a random shortcut from OneDrive Desktop
                        selected_shortcut = random.choice(onedrive_shortcuts)

                        # Ask the user if they want to open the selected shortcut
                        os.startfile(os.path.join(onedrive_path, selected_shortcut))
                        
                    else:
                        # No shortcut files found in the OneDrive Desktop folder
{