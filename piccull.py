from tkinter import Tk, Button, Frame, Label, Checkbutton, filedialog, StringVar, IntVar, DISABLED, Toplevel
import os
import shutil
import subprocess
import platform
from PIL import ImageTk, Image

class PicCull:
    def __init__(self, master):
        self.master = master
        self.master.title('PicCull')

        self.index = 0
        self.image_paths = []
        self.directory_path = ""
        self.culled_dir = None
        self.delete_on_cull = IntVar()

        self.img_label = Label(master)
        self.img_label.pack()

        button_frame = Frame(master)
        button_frame.pack()

        Button(button_frame, text="Load Directory", command=self.open_directory).grid(row=0, column=0)

        self.btn_open_culled = Button(button_frame, text="Open Culled Folder", command=self.open_culled_folder, state=DISABLED)
        self.btn_open_culled.grid(row=0, column=1)

        Button(button_frame, text="Settings", command=self.open_settings).grid(row=0, column=2)

        frame = Frame(master)
        frame.pack()

        self.btn_prev = Button(frame, text="<- Prev", command=self.prev_image, state=DISABLED)
        self.btn_prev.grid(row=0, column=0)

        self.btn_cull = Button(frame, text="Cull", command=self.cull_image, state=DISABLED)
        self.btn_cull.grid(row=0, column=1)

        self.btn_next = Button(frame, text="Next ->", command=self.next_image, state=DISABLED)
        self.btn_next.grid(row=0, column=2)

        self.master.bind('<Left>', lambda e: self.prev_image())
        self.master.bind('<Right>', lambda e: self.next_image())
        self.master.bind('<Down>', lambda e: self.cull_image())

        # Status Bar
        self.status_var = StringVar()
        self.status_bar = Label(master, textvariable=self.status_var, bd=1, relief='sunken', anchor='w')
        self.status_bar.pack(side='bottom', fill='x')

    def open_directory(self):
        self.index = 0
        self.directory_path = filedialog.askdirectory(initialdir="/", title="Select a Directory")

        if not self.directory_path:
            self.status_var.set("No directory selected.")
            return

        self.culled_dir = os.path.join(self.directory_path, 'pic-culled')
        self.btn_open_culled.config(state='normal' if os.path.exists(self.culled_dir) else 'disabled')

        self.image_paths = list(filter(lambda f: f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')), os.listdir(self.directory_path)))
        self.image_paths = [os.path.join(self.directory_path, f) for f in self.image_paths]

        if not self.image_paths:
            self.status_var.set("No images found in the selected directory.")
            return

        self.status_var.set(f"Loaded directory: {self.directory_path}. Image {self.index+1}/{len(self.image_paths)}")
        self.show_image()

    def open_culled_folder(self):
        if self.culled_dir and os.path.exists(self.culled_dir):
            if platform.system() == "Windows":
                os.startfile(self.culled_dir)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", self.culled_dir])
            else:
                subprocess.Popen(["xdg-open", self.culled_dir])
        else:
            self.status_var.set("No culled directory exists.")

    def open_settings(self):
        settings_window = Toplevel(self.master)
        settings_window.title("Settings")
        Checkbutton(settings_window, text="Delete on cull", variable=self.delete_on_cull).pack()

    def show_image(self):
        if self.index < len(self.image_paths):
            img_path = self.image_paths[self.index]

            try:
                img = Image.open(img_path)
            except IOError:
                self.status_var.set(f"Unable to open image at {img_path}. It might be corrupted.")
                self.update_button_states()
                return

            img.thumbnail((800, 600))
            photo = ImageTk.PhotoImage(img)
            self.img_label.configure(image=photo)
            self.img_label.image = photo
            self.status_var.set(f"Directory: {self.directory_path}. Image {self.index+1}/{len(self.image_paths)}")
        else:
            self.img_label.configure(image=None)
            self.img_label.image = None
            self.status_var.set("No more images in the directory.")
        self.update_button_states()

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
            self.btn_open_culled.config(state='normal')  # The culled folder should now exist.
            self.show_image()

    def prev_image(self):
        if self.index > 0:
            self.index -= 1
            self.update_button_states()
            self.show_image()

    def next_image(self):
        if self.index < len(self.image_paths) - 1:
            self.index += 1
            self.update_button_states()
            self.show_image()

    def update_button_states(self):
        if self.index <= 0:
            self.btn_prev.config(state='disabled')
        else:
            self.btn_prev.config(state='normal')

        if self.index >= len(self.image_paths) - 1:
            self.btn_next.config(state='disabled')
        else:
            self.btn_next.config(state='normal')

        if len(self.image_paths) == 0:
            self.btn_cull.config(state='disabled')
        else:
            self.btn_cull.config(state='normal')

root = Tk()
app = PicCull(root)
root.mainloop()
