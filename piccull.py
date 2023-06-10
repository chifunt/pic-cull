from tkinter import filedialog, StringVar, IntVar
import customtkinter as ctk
import os
import shutil
import subprocess
import platform
from PIL import Image

class PicCull:
    def __init__(self, master):
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
        self.master = master
        self.master.title('PicCull')
        root.geometry('600x800')
        root.minsize(480, 480)
        # root.iconbitmap('icon.ico')
        ctk.set_default_color_theme('dark-blue')

    def create_widgets(self):
        self.create_image_label()
        self.create_util_buttons()
        self.create_nav_cull_buttons()

    def create_image_label(self):
        self.img_label = ctk.CTkLabel(self.master, text="No image loaded.")
        self.img_label.pack()

    def create_util_buttons(self):
        utilbuttons_frame = self.create_frame(self.master)
        self.create_button(utilbuttons_frame, "Load Directory", self.open_directory, 0)
        self.btn_open_culled = self.create_button(utilbuttons_frame, "Open Culled Folder", self.open_culled_folder, 1, state='disabled')
        self.create_button(utilbuttons_frame, "Settings", self.open_settings, 2)

    def create_nav_cull_buttons(self):
        navcullbuttons_frame = self.create_frame(self.master)
        self.btn_prev = self.create_button(navcullbuttons_frame, "<- Prev", self.prev_image, 0, state='disabled')
        self.btn_cull = self.create_button(navcullbuttons_frame, "Cull", self.cull_image, 1, state='disabled', fg_color='red', hover_color='#8B0000')
        self.btn_next = self.create_button(navcullbuttons_frame, "Next ->", self.next_image, 2, state='disabled')

    def create_frame(self, master):
        frame = ctk.CTkFrame(master)
        frame.pack()
        return frame

    def create_button(self, master, text, command, column, state='normal', **kwargs):
        button = ctk.CTkButton(master, text=text, command=command, border_width=2, state=state, **kwargs)
        button.grid(row=0, column=column, padx=10, pady=10)
        return button

    def create_keybindings(self):
        self.keybindings = {"prev_image": "<Left>", "next_image": "<Right>", "cull_image": "<Down>"}
        self.keybindings_entries = {}
        for action in self.keybindings:
            self.master.bind(self.keybindings[action], lambda e, action=action: getattr(self, action)())

    def create_status_bar(self):
        self.status_var = StringVar()
        self.status_bar = ctk.CTkLabel(self.master, textvariable=self.status_var, anchor='center', bg_color='gray')
        self.status_bar.pack(side='bottom', fill='x')

    def get_directory(self):
        directory_path = filedialog.askdirectory(initialdir="/", title="Select a Directory")
        if not directory_path:
            raise Exception("No directory selected.")
        return directory_path

    def load_image_paths(self, directory_path):
        image_paths = list(filter(lambda f: f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')), os.listdir(directory_path)))
        image_paths = [os.path.join(directory_path, f) for f in image_paths]
        if not image_paths:
            raise Exception("No images found in the selected directory.")
        return image_paths

    # Open a directory and load all image files from it
    def open_directory(self):
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

    # Open the folder containing the culled images
    def open_culled_folder(self):
        if self.culled_dir and os.path.exists(self.culled_dir):
            if platform.system() == 'Windows':
                os.startfile(self.culled_dir)
            elif platform.system() == 'Darwin':
                subprocess.Popen(["open", self.culled_dir])
            else:
                subprocess.Popen(['xdg-open', self.culled_dir])
        else:
            self.status_var.set("No culled directory exists.")

    # Open a settings window
    def open_settings(self):
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
        for action, entry in self.keybindings_entries.items():
            self.keybindings[action] = entry.get()

        # Unbind all key events
        for action in self.keybindings:
            self.master.unbind(self.keybindings[action])

        # Re-bind the key events
        self.master.bind(self.keybindings["prev_image"], lambda e: self.prev_image())
        self.master.bind(self.keybindings["next_image"], lambda e: self.next_image())
        self.master.bind(self.keybindings["cull_image"], lambda e: self.cull_image())

    # Display the current image
    def show_image(self):
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

    # Cull the current image
    def cull_image(self):
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

    # Display the previous image
    def prev_image(self):
        if self.index > 0:
            self.index -= 1
            self.update_button_states()
            self.show_image()

    # Display the next image
    def next_image(self):
        if self.index < len(self.image_paths) - 1:
            self.index += 1
            self.update_button_states()
            self.show_image()

    # Update the state of the buttons
    def update_button_states(self):
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
