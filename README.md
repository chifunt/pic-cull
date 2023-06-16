# PicCull 🥒

PicCull is a user-friendly desktop application designed to streamline your image management process. It provides an intuitive, easy-to-navigate interface that enables users to quickly and efficiently view and cull images in a directory.

## Features
- Navigate through a directory of images
- Delete the image or move it to a separate 'culled' folder
- Apply custom keybindings for certain actions
- Modify some settings

## Prerequisites
- Python 3.x
- tkinter
- PIL (Pillow)

## How to Run

1. Clone the repository to your local machine:

```bash
git clone https://github.com/Chifunt/piccull
```

2. Navigate into the cloned repository:

```bash
cd piccull
```

3. Run the application:

```bash
python piccull.py
```

Note: Replace "python" with "python3" if you have both Python 2.x and Python 3.x installed on your machine.

## Usage

- Use the "Load Directory" button to select the directory containing the images you wish to manage.
- Navigate through the images using the "<- Prev" and "Next ->" buttons.
- Cull an image using the "Cull" button. This will either delete the image or move it to a separate 'culled' folder, depending on your settings.
- Open the 'culled' folder using the "Open Culled Folder" button.
- Modify the keybindings and culling behavior in the "Settings" window.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
