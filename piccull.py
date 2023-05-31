from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog
import os

class ImagePreviewer:
    def __init__(self, master):
        self.master = master
        self.master.title('PicCull')
        
        self.index = 0
        self.image_paths = []

        self.img_label = Label(master)
        self.img_label.pack()

        Button(master, text="Open Directory", command=self.open_directory).pack()

        frame = Frame(master)
        frame.pack()

        Button(frame, text="Delete", command=self.delete_image).grid(row=0, column=0)
        Button(frame, text="<- Prev", command=self.prev_image).grid(row=0, column=1)
        Button(frame, text="Next ->", command=self.next_image).grid(row=0, column=2)
        Button(frame, text="Skip", command=self.skip_image).grid(row=0, column=3)

        self.master.bind('<Left>', lambda e: self.prev_image())
        self.master.bind('<Right>', lambda e: self.next_image())
        self.master.bind('<Up>', lambda e: self.skip_image())
        self.master.bind('<Down>', lambda e: self.delete_image())

    def open_directory(self):
        self.index = 0
        directory_path = filedialog.askdirectory(initialdir="/", title="Select a Directory")
        if directory_path:
            self.image_paths = list(filter(lambda f: f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')), os.listdir(directory_path)))
            self.image_paths = [os.path.join(directory_path, f) for f in self.image_paths]
            self.show_image()

    def show_image(self):
        if self.index < len(self.image_paths):
            img_path = self.image_paths[self.index]
            img = Image.open(img_path)
            img.thumbnail((800, 600))
            photo = ImageTk.PhotoImage(img)
            self.img_label.configure(image=photo)
            self.img_label.image = photo
        else:
            self.img_label.configure(image=None)
            self.img_label.image = None

    def delete_image(self):
        if self.index < len(self.image_paths):
            os.remove(self.image_paths[self.index])
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
app = ImagePreviewer(root)
root.mainloop()
