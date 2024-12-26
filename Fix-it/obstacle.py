from PIL import Image, ImageTk  # type: ignore


class Obstacle:
    def __init__(self, canvas, x, y, image_path, platforms):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.platforms = platforms
        self.current_platform = 0
        self.image = Image.open(image_path).resize((30, 30),
                                                   Image.Resampling.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(self.image)
        self.image_id = self.canvas.create_image(self.x, self.y, anchor="nw",
                                                 image=self.photo_image)
        self.move_speed = 10

    def move(self):
        self.x -= self.move_speed
        if self.x < -50:
            self.canvas.delete(self.image_id)
            return False

        if self.x < 0 and self.current_platform < len(self.platforms) - 1:
            self.current_platform += 1
            self.x = 1200  # Reset x position to the right side of the screen
            self.y = self.platforms[self.current_platform]

        self.canvas.coords(self.image_id, self.x, self.y)
        return True

    def get_position(self):
        return self.canvas.bbox(self.image_id)

    def delete(self):
        self.canvas.delete(self.image_id)

    def render(self):
        if self.image_id is None:
            self.image_id = self.canvas.create_image(self.x, self.y,
                                                     anchor="nw",
                                                     image=self.image)
        else:
            self.canvas.coords(self.image_id, self.x, self.y)
