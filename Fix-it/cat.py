from PIL import Image, ImageTk  # type: ignore
from settings import SCREEN_WIDTH
import random


class Cat:
    def __init__(self, canvas, x, y, calico_right, calico_left,
                 pause_state, speed):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.current_frame = 0
        self.direction = "left"
        self.is_running = True
        self.pause_state = pause_state

        # Load the running sprite sheets for both directions
        self.run_frames_right = self.load_frames(calico_right,
                                                 frame_width=36,
                                                 frame_height=31)
        self.run_frames_left = self.load_frames(calico_left,
                                                frame_width=36,
                                                frame_height=31)

        self.photo_image = self.run_frames_left[self.current_frame]
        self.image_cat = self.canvas.create_image(self.x, self.y, anchor="nw",
                                                  image=self.photo_image)

        self.animation_speed = 100
        self.move_speed = speed  # Speed of movement
        self.y_position = [150, 400, 650]

        self.animate()
        self.random_move()  # Start random movement

    # Load frames from a sprite sheet
    def load_frames(self, sheet_path, frame_width, frame_height):
        sheet = Image.open(sheet_path)
        sheet_width, sheet_height = sheet.size
        frames = []

        # Calculate the number of frames in each row
        frames_per_row = sheet_width // frame_width

        # Extract frames from both rows
        for row in range(2):  # Assuming there are two rows
            for col in range(frames_per_row):
                left = col * frame_width
                top = row * frame_height
                right = left + frame_width
                bottom = top + frame_height

                frame = sheet.crop((left, top, right, bottom))
                frame = frame.resize((frame_width * 2, frame_height * 2),
                                     Image.Resampling.LANCZOS)
                frames.append(ImageTk.PhotoImage(frame))

        return frames

    def animate(self):
        if self.pause_state():
            self.canvas.after(self.animation_speed, self.animate)
            return
        self.current_frame = (
            (self.current_frame + 1)
            % len(self.run_frames_right)
        )
        self.photo_image = (
            self.run_frames_right
            if self.direction == "right"
            else self.run_frames_left
        )[self.current_frame]
        self.canvas.itemconfig(self.image_cat, image=self.photo_image)
        self.canvas.after(self.animation_speed, self.animate)

    def random_move(self):
        if self.pause_state():
            self.canvas.after(1000, self.random_move)
            return
        self.y = random.choice(self.y_position)
        self.canvas.coords(self.image_cat, self.x, self.y)

        if random.choice([True, False]):
            self.target_x = SCREEN_WIDTH - 300
            self.direction = "right"
        else:
            self.target_x = -100
            self.direction = "left"

        self.update_position()

    def get_position(self):
        """Return the bounding box of the cat as (x1, y1, x2, y2)."""
        # Get the image's bounding box
        bbox = self.canvas.bbox(self.image_cat)
        return bbox

    def update_position(self):
        if self.pause_state():
            self.canvas.after(50, self.update_position)
            return
        # Move horizontally on the current platform
        dx = self.target_x - self.x
        if abs(dx) < self.move_speed:
            # Reached target; switch to another platform after a delay
            self.canvas.after(1000, self.random_move)
            return

        # Update direction and position
        self.direction = "right" if dx > 0 else "left"
        self.x += self.move_speed if dx > 0 else -self.move_speed

        self.canvas.coords(self.image_cat, self.x, self.y)
        self.canvas.after(50, self.update_position)

    def render(self):
        if self.image_id is None:
            self.image_id = self.canvas.create_image(self.x, self.y,
                                                     anchor="nw",
                                                     image=self.current_sprite)
        else:
            self.canvas.coords(self.image_id, self.x, self.y)
