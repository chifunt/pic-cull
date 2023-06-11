"""
This module implements the PicCull application, a simple GUI tool for image culling.

The PicCull application allows users to navigate through a directory of images
and either delete the image or move it to a separate 'culled' folder. The user can also
apply custom keybindings for certain actions and modify some settings.

The application uses the tkinter library for the graphical user interface and
the PIL (Pillow) library for image handling.
"""

from tkinter import filedialog, StringVar, IntVar
import os
import shutil
import subprocess
import platform
import customtkinter as ctk
from PIL import Image

class PicCull:
    def __init__(self, master):
        """
        Initializes an instance of the PicCull application.

        :param master: The root window for the application.
        """
        self.master = master
        self.index = 0
        self.image_paths = []
        self.directory_path = ""
        self.culled_dir = None
        self.delete_on_cull = IntVar()
        self.img_label = None
        self.btn_open_culled = None
        self.btn_prev = None
        self.btn_cull = None
        self.btn_next = None
        self.keybindings = None
        self.keybindings_entries = None
        self.status_var = None
        self.status_bar = None

        self.init_master(master)
        self.create_widgets()
        self.create_keybindings()
        self.create_status_bar()

    def init_master(self, master):
        """
        Initialize the main application window with certain attributes and configurations.

        :param master: The root window for the application.
        """
        self.master = master
        self.master.title('PicCull')
        root.geometry('600x800')
        root.minsize(480, 480)
        # root.iconbitmap('icon.ico')
        ctk.set_default_color_theme('dark-blue')

    def create_widgets(self):
        """
        Creates the main widgets of the application which include the image label and utility buttons.
        """
        self.create_image_label()
        self.create_util_buttons()
        self.create_nav_cull_buttons()

    def create_image_label(self):
        """
        Creates a label to display the image.
        """
        self.img_label = ctk.CTkLabel(self.master, text="No image loaded.")
        self.img_label.pack()

    def create_util_buttons(self):
        """
        Creates the utility buttons (Load Directory, Open Culled Folder, Settings) for the application.
        """
        utilbuttons_frame = self.create_frame(self.master)
        self.create_button(utilbuttons_frame, "Load Directory", self.open_directory, 0)
        self.btn_open_culled = self.create_button(utilbuttons_frame, "Open Culled Folder", self.open_culled_folder, 1, state='disabled')
        self.create_button(utilbuttons_frame, "Settings", self.open_settings, 2)

    def create_nav_cull_buttons(self):
        """
        Creates the navigation and cull buttons (Prev, Cull, Next) for the application.
        """
        navcullbuttons_frame = self.create_frame(self.master)
        self.btn_prev = self.create_button(navcullbuttons_frame, "<- Prev", self.prev_image, 0, state='disabled')
        self.btn_cull = self.create_button(navcullbuttons_frame, "Cull", self.cull_image, 1, state='disabled', fg_color='red', hover_color='#8B0000')
        self.btn_next = self.create_button(navcullbuttons_frame, "Next ->", self.next_image, 2, state='disabled')

    def create_frame(self, master):
        """
        Creates a new frame in the application.

        :param master: The parent widget.
        :return: The newly created frame.
        """
        frame = ctk.CTkFrame(master)
        frame.pack()
        return frame

    def create_button(self, master, text, command, column, state='normal', **kwargs):
        """
        Creates a new button in the application.

        :param master: The parent widget.
        :param text: Text to display on the button.
        :param command: Function to execute when the button is clicked.
        :param column: The column where to place the button in the grid.
        :param state: The initial state of the button. Default is 'normal'.
        :param kwargs: Additional parameters for the button.
        :return: The newly created button.
        """
        button = ctk.CTkButton(master, text=text, command=command, border_width=2, state=state, **kwargs)
        button.grid(row=0, column=column, padx=10, pady=10)
        return button

    def create_keybindings(self):
        """
        Creates keybindings for certain actions in the application.
        """
        self.keybindings = {"prev_image": "<Left>", "next_image": "<Right>", "cull_image": "<Down>"}
        self.keybindings_entries = {}
        for action in self.keybindings:
            self.master.bind(self.keybindings[action], lambda e, action=action: getattr(self, action)())

    def create_status_bar(self):
        """
        Creates a status bar at the bottom of the application window.
        """
        self.status_var = StringVar()
        self.status_bar = ctk.CTkLabel(self.master, textvariable=self.status_var, anchor='center', bg_color='gray')
        self.status_bar.pack(side='bottom', fill='x')

    def get_directory(self):
        """
        Opens a file dialog to select a directory.

        :return: The path of the selected directory.
        """
        directory_path = filedialog.askdirectory(initialdir="/", title="Select a Directory")
        if not directory_path:
            raise Exception("No directory selected.")
        return directory_path

    def load_image_paths(self, directory_path):
        """
        Loads all image files from a given directory.

        :param directory_path: The directory from which to load image files.
        :return: List of paths to the image files.
        """
        image_paths = list(filter(lambda f: f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')), os.listdir(directory_path)))
        image_paths = [os.path.join(directory_path, f) for f in image_paths]
        if not image_paths:
            raise Exception("No images found in the selected directory.")
        return image_paths

    def open_directory(self):
        """
        Opens a directory and loads all image files from it.
        """
        try:
            self.index = 0
            self.directory_path = self.get_directory()

            self.culled_dir = os.path.join(self.directory_path, 'pic-culled')
            self.btn_open_culled.configure(state='normal' if os.path.exists(self.culled_dir) else 'disabled')

            self.image_paths = self.load_image_paths(self.directory_path)

            self.status_var.set(f"Loaded directory: {self.directory_path}. Image {self.index+1}/{len(self.image_paths)}")
            self.show_image()

        except Exception as e:
            self.status_var.set(str(e))

    def open_culled_folder(self):
        """
        Opens the folder containing the culled images.
        """
        if self.culled_dir and os.path.exists(self.culled_dir):
            if platform.system() == 'Windows':
                os.startfile(self.culled_dir)
            elif platform.system() == 'Darwin':
                subprocess.Popen(["open", self.culled_dir])
            else:
                subprocess.Popen(['xdg-open', self.culled_dir])
        else:
            self.status_var.set("No culled directory exists.")

    def open_settings(self):
        """
        Opens a settings window for the application.
        """
        pad_x = 10
        pad_y = 10
        settings_window = ctk.CTkToplevel(self.master)
        settings_window.title("Piccull Settings")
        settings_window.grab_set()

        shortcuts_label = ctk.CTkLabel(settings_window, text="Shortcuts:")
        shortcuts_label.grid(row=0, column=0, columnspan=2, padx=pad_x, pady=pad_y)

        self.keybindings_entries.clear()
        for idx, (action, key) in enumerate(self.keybindings.items()):
            label = ctk.CTkLabel(settings_window, text=f"{action}:")
            label.grid(row=1+idx, column=0, sticky='w', padx=pad_x, pady=pad_y)

            entry = ctk.CTkEntry(settings_window)
            entry.grid(row=1+idx, column=1, padx=pad_x, pady=pad_y)
            entry.insert(0, key)

            self.keybindings_entries[action] = entry

        delete_checkbox = ctk.CTkCheckBox(settings_window, text="Delete on cull", variable=self.delete_on_cull)
        delete_checkbox.grid(row=1+len(self.keybindings), column=0, columnspan=2, padx=pad_x, pady=pad_y)

        apply_button = ctk.CTkButton(settings_window, text="Apply", command=self.apply_settings)
        apply_button.grid(row=2+len(self.keybindings), column=0, columnspan=2, padx=pad_x, pady=pad_y)

    def apply_settings(self):
        """
        Applies the changes made in the settings window.
        """
        for action, entry in self.keybindings_entries.items():
            self.keybindings[action] = entry.get()

        # Unbind all key events
        for action in self.keybindings:
            self.master.unbind(self.keybindings[action])

        # Re-bind the key events
        self.master.bind(self.keybindings["prev_image"], lambda e: self.prev_image())
        self.master.bind(self.keybindings["next_image"], lambda e: self.next_image())
        self.master.bind(self.keybindings["cull_image"], lambda e: self.cull_image())

    def show_image(self):
        """
        Displays the current image in the application.
        """
        if self.index < len(self.image_paths):
            img_path = self.image_paths[self.index]

            try:
                img = Image.open(img_path)
            except IOError:
                self.status_var.set(f"Unable to open image at {img_path}. It might be corrupted.")
                self.update_button_states()
                return

            width, height = img.size
            ratio = min(800 / width, 600 / height)

            photo = ctk.CTkImage(img, size=(int(width * ratio), int(height * ratio)))
            self.img_label.configure(image=photo, text="")
            self.img_label.configure(image=photo)
            self.img_label.image = photo
            self.status_var.set(f"Directory: {self.directory_path}. Image {self.index+1}/{len(self.image_paths)}")
        else:
            self.img_label.configure(image=None, text="No image loaded.")
            self.img_label.configure(image=None)
            self.img_label.image = None
            self.status_var.set("No more images in the directory.")
        self.update_button_states()

    def cull_image(self):
        """
        Culls the current image. The image is either deleted or moved to a 'culled' folder.
        """
        if self.index < len(self.image_paths):
            if not os.path.exists(self.culled_dir):
                os.makedirs(self.culled_dir)

            if self.delete_on_cull.get():
                os.remove(self.image_paths[self.index])
            else:
                shutil.move(self.image_paths[self.index], self.culled_dir)

            del self.image_paths[self.index]
            self.update_button_states()
            self.btn_open_culled.configure(state='normal')
            self.show_image()

    def prev_image(self):
        """
        Displays the previous image in the application.
        """
        if self.index > 0:
            self.index -= 1
            self.update_button_states()
            self.show_image()

    def next_image(self):
        """
        Displays the next image in the application.
        """
        if self.index < len(self.image_paths) - 1:
            self.index += 1
            self.update_button_states()
            self.show_image()

    def update_button_states(self):
        """
        Updates the state of the navigation and cull buttons based on the current image index.
        """
        if self.index <= 0:
            self.btn_prev.configure(state='disabled')
        else:
            self.btn_prev.configure(state='normal')

        if self.index >= len(self.image_paths) - 1:
            self.btn_next.configure(state='disabled')
        else:
            self.btn_next.configure(state='normal')

        if len(self.image_paths) == 0:
            self.btn_cull.configure(state='disabled')
        else:
            self.btn_cull.configure(state='normal')

# Initialize the application
root = ctk.CTk()
app = PicCull(root)
# Start the application's main loop
root.mainloop()
