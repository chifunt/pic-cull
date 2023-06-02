from tkinter import Tk, Button, Frame, Label, filedialog, StringVar
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

        self.img_label = Label(master)
        self.img_label.pack()

        Button(master, text="Load Directory", command=self.open_directory).pack()
        Button(master, text="Open Culled Folder", command=self.open_culled_folder).pack()

        frame = Frame(master)
        frame.pack()

        Button(frame, text="Cull", command=self.cull_image).grid(row=0, column=0)
        Button(frame, text="<- Prev", command=self.prev_image).grid(row=0, column=1)
        Button(frame, text="Next ->", command=self.next_image).grid(row=0, column=2)
        Button(frame, text="Skip", command=self.skip_image).grid(row=0, column=3)

        self.master.bind('<Left>', lambda e: self.prev_image())
        self.master.bind('<Right>', lambda e: self.next_image())
        self.master.bind('<Up>', lambda e: self.skip_image())
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

    def show_image(self):
        if self.index < len(self.image_paths):
            img_path = self.image_paths[self.index]
            
            try:
                img = Image.open(img_path)
            except IOError:
                self.status_var.set(f"Unable to open image at {img_path}. It might be corrupted.")
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

    def cull_image(self):
        if self.index < len(self.image_paths):
            if not os.path.exists(self.culled_dir):
                os.makedirs(self.culled_dir)

            shutil.move(self.image_paths[self.index], self.culled_dir)
            del self.image_paths[self.index]
            self.show_image()

    def skip_image(self):
        self.index += 1
        self.show_image()

    def prev_image(self):
        if self.index > 0:
            self.index -= 1
            self.show_image()

    def next_image(self):
        if self.index < len(self.image_paths) - 1:
            self.index += 1
            self.show_image()

root = Tk()
app = PicCull(root)
root.mainloop()
