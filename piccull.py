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
        self.master.title('PicCull')
        root.geometry('600x800')
        root.minsize(480, 480)
        ctk.set_default_color_theme('dark-blue')

        # Initialize variables
        self.index = 0
        self.image_paths = []
        self.directory_path = ""
        self.culled_dir = None
        self.delete_on_cull = IntVar()

        # Create widgets for displaying the image and buttons for interacting with the application
        self.img_label = ctk.CTkLabel(master, text="No image loaded.")
        self.img_label.pack()

        # Set padding for x and y axis (in pixels)
        pad_x = 10
        pad_y = 10

        utilbuttons_frame = ctk.CTkFrame(master)
        utilbuttons_frame.pack()

        self.btn_loaddir = ctk.CTkButton(utilbuttons_frame, text="Load Directory", command=self.open_directory, border_width=2)
        self.btn_loaddir.grid(row=0, column=0, padx=pad_x, pady=pad_y)

        self.btn_open_culled = ctk.CTkButton(utilbuttons_frame, text="Open Culled Folder", command=self.open_culled_folder, state='disabled', border_width=2)
        self.btn_open_culled.grid(row=0, column=1, padx=pad_x, pady=pad_y)

        self.btn_settings = ctk.CTkButton(utilbuttons_frame, text="Settings", command=self.open_settings, border_width=2)
        self.btn_settings.grid(row=0, column=2, padx=pad_x, pady=pad_y)

        navcullbuttons_frame = ctk.CTkFrame(master)
        navcullbuttons_frame.pack()

        self.btn_prev = ctk.CTkButton(navcullbuttons_frame, text="<- Prev", command=self.prev_image, state='disabled', border_width=2)
        self.btn_prev.grid(row=0, column=0, padx=pad_x, pady=pad_y)

        self.btn_cull = ctk.CTkButton(navcullbuttons_frame, text="Cull", command=self.cull_image, state='disabled', border_width=2, fg_color='red', hover_color='#8B0000')
        self.btn_cull.grid(row=0, column=1, padx=pad_x, pady=pad_y)

        self.btn_next = ctk.CTkButton(navcullbuttons_frame, text="Next ->", command=self.next_image, state='disabled', border_width=2)
        self.btn_next.grid(row=0, column=2, padx=pad_x, pady=pad_y)

        # Initialize keybindings and keybindings_entries
        self.keybindings = {
            "prev_image": "<Left>",
            "next_image": "<Right>",
            "cull_image": "<Down>"
        }
        self.keybindings_entries = {}

        # Bind keyboard events to functions
        self.master.bind('<Left>', lambda e: self.prev_image())
        self.master.bind('<Right>', lambda e: self.next_image())
        self.master.bind('<Down>', lambda e: self.cull_image())

        # Create status bar at the bottom of the window
        self.status_var = StringVar()
        self.status_bar = ctk.CTkLabel(master, textvariable=self.status_var, anchor='center', bg_color='gray')
        self.status_bar.pack(side='bottom', fill='x')

    # Open a directory and load all image files from it
    def open_directory(self):
        self.index = 0
        self.directory_path = filedialog.askdirectory(initialdir="/", title="Select a Directory")

        if not self.directory_path:
            self.status_var.set("No directory selected.")
            return

        self.culled_dir = os.path.join(self.directory_path, 'pic-culled')
        self.btn_open_culled.configure(state='normal' if os.path.exists(self.culled_dir) else 'disabled')

        self.image_paths = list(filter(lambda f: f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')), os.listdir(self.directory_path)))
        self.image_paths = [os.path.join(self.directory_path, f) for f in self.image_paths]

        if not self.image_paths:
            self.status_var.set("No images found in the selected directory.")
            return

        self.status_var.set(f"Loaded directory: {self.directory_path}. Image {self.index+1}/{len(self.image_paths)}")
        self.show_image()

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
