import tkinter as tk
from PIL import Image, ImageTk  # type: ignore


class Stall:
    def __init__(self, canvas, x, y, fixed_img, unfixed_img, points):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.points = points

        # Load images using PIL Image
        self.fixed_image = Image.open(fixed_img)
        self.unfixed_image = Image.open(unfixed_img)

        # Resize the images before converting to PhotoImage
        self.fixed_image = self.fixed_image.resize((180, 195),
                                                   Image.Resampling.LANCZOS
                                                   )
        self.unfixed_image = self.unfixed_image.resize((180, 195),
                                                       Image.Resampling.LANCZOS
                                                       )

        # Convert PIL Image to PhotoImage
        self.fixed_img = ImageTk.PhotoImage(self.fixed_image)
        self.unfixed_img = ImageTk.PhotoImage(self.unfixed_image)

        # Set the current image to the fixed image initially
        self.current_img = self.fixed_img
        self.img_id = canvas.create_image(self.x, self.y, anchor="nw",
                                          image=self.current_img)

    def make_unfixed(self):
        # Switch to the unfixed image
        self.current_img = self.unfixed_img
        self.canvas.itemconfig(self.img_id, image=self.current_img)

    def make_fixed(self):
        # Switch to the fixed image
        self.current_img = self.fixed_img
        self.canvas.itemconfig(self.img_id, image=self.current_img)

    def get_position(self):
        # Get position of the image from the canvas
        return self.canvas.bbox(self.img_id)

    def render(self):
        if self.current_img and self.canvas:
            self.image_id = self.canvas.create_image(self.x, self.y,
                                                     image=self.current_img,
                                                     anchor=tk.NW)
