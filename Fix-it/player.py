from PIL import Image, ImageTk  # type: ignore
import tkinter as tk


class Player:
    def __init__(self, canvas, x, y, idle_sprite_path,
                 run_sprite_sheet_path_right, run_sprite_sheet_path_left,
                 scoring):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.scoring = scoring
        self.health = 3
        self.current_frame = 0
        self.is_running = False
        self.is_jumping = False
        self.jump_speed = -15
        self.gravity = 1
        self.jump_height = 0
        self.direction = None  # Initialize direction
        self.platforms = [150, 400, 650]

        # Load idle frame
        self.idle_image = Image.open(idle_sprite_path).resize(
            (91, 129), Image.Resampling.LANCZOS)
        self.idle_photo_image = ImageTk.PhotoImage(self.idle_image)

        # Load running sprite sheets and split into frames
        self.run_frames_right = self.load_frames(run_sprite_sheet_path_right,
                                                 frame_width=128)
        self.run_frames_left = self.load_frames(run_sprite_sheet_path_left,
                                                frame_width=128)

        self.photo_image = self.idle_photo_image
        self.image_john = self.canvas.create_image(self.x, self.y, anchor="nw",
                                                   image=self.photo_image)

        self.animation_speed = 100
        self.animate()  # Start animation loop

    def load_frames(self, sheet_path, frame_width, frame_height=129):
        sheet = Image.open(sheet_path)
        sheet_width, sheet_height = sheet.size
        frames = []

        for i in range(0, sheet_width, frame_width):
            frame = sheet.crop((i, 0, i + frame_width, sheet_height))
            resized_frame = frame.resize((frame_width, frame_height),
                                         Image.Resampling.LANCZOS)
            frames.append(ImageTk.PhotoImage(resized_frame))

        return frames

    def animate(self):
        """Update the animation frame based on movement state."""
        if self.is_running:
            self.current_frame = (self.current_frame + 1) % \
                                 len(self.run_frames_right)
            if self.direction == "left":
                self.photo_image = self.run_frames_left[self.current_frame]
            else:
                self.photo_image = self.run_frames_right[self.current_frame]
        else:
            self.photo_image = self.idle_photo_image

        self.canvas.itemconfig(self.image_john, image=self.photo_image)
        self.canvas.after(self.animation_speed, self.animate)

    def update(self):
        """Update the player's position on the canvas."""
        self.canvas.coords(self.image_john, self.x, self.y)

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_height = self.jump_speed
            self.update_jump()

    def update_jump(self):
        if self.is_jumping:
            # Update vertical position and velocity
            self.y += self.jump_height
            self.jump_height += self.gravity

            # Check if the player is descending and should land
            if self.jump_height > 0:  # Descending phase
                nearest_platform = None
                for platform in sorted(self.platforms):  # Bottom to top
                    if (self.y < platform and
                            (platform - self.y <= abs(self.jump_height))):
                        nearest_platform = platform
                        break  # Found the nearest platform

                if nearest_platform is not None:
                    self.y = nearest_platform
                    self.is_jumping = False

            # Ensure the player doesn't go below the lowest platform (ground)
            if self.y > max(self.platforms):
                self.y = max(self.platforms)
                self.is_jumping = False

            # Update the player's position on the canvas
            self.canvas.coords(self.image_john, self.x, self.y)

            # Continue the jump if still active
            if self.is_jumping:
                self.canvas.after(16, self.update_jump)

    def move_left(self):
        if self.x > 100:
            self.is_running = True
            self.direction = "left"
            self.x -= 10
            self.update()

    def move_right(self):
        if self.x < 1350:
            self.is_running = True
            self.direction = "right"
            self.x += 10
            self.update()

    def stop_running(self):
        self.is_running = False
        self.direction = None

    def move_up(self):
        if 350 < self.y < 450:
            self.y -= 250
            self.update()
        elif 550 < self.y < 700:
            self.y -= 250
            self.update()

    def move_down(self):
        if 100 < self.y < 250:
            self.y += 250
            self.update()
        elif 350 < self.y < 450:
            self.y += 250
            self.update()

    def check_collision(self, box1, box2):
        x1_min, y1_min, x1_max, y1_max = box1
        x2_min, y2_min, x2_max, y2_max = box2

        return not (x1_max < x2_min or x1_min > x2_max or
                    y1_max < y2_min or y1_min > y2_max)

    # Define the show_score_increment method
    def show_score_increment(self, x, y, increment):
        score_text = self.canvas.create_text(x, y, text=f"+{increment}",
                                             font=("Arial", 16), fill="yellow")

        def fade_out(opacity):
            if opacity > 0:
                self.canvas.itemconfig(score_text,
                                       fill=f"#{opacity:02x}{opacity:02x}00")
                self.canvas.after(50, fade_out, opacity - 5)
            else:
                self.canvas.delete(score_text)

        fade_out(255)

    def interact_stall(self, stalls):
        global stall
        player_box = self.get_position()
        for stall in stalls:
            stall_box = stall.get_position()
            if self.check_collision(player_box, stall_box):
                stall.make_fixed()
                self.scoring.update_score(stall.points)
                self.show_score_increment(self.x, self.y, stall.points)

    def get_position(self):
        """Return the bounding box of the player as (x1, y1, x2, y2)."""
        bbox = self.canvas.bbox(self.image_john)
        return bbox

    def render(self):
        """Render the player on the canvas if not already present."""
        if self.canvas:
            # Ensure the player image is updated or created
            if not hasattr(self, "image_id") or self.image_id is None:
                self.image_id = self.canvas.create_image(
                    self.x, self.y, image=self.idle_photo_image, anchor=tk.NW
                )
            else:
                self.canvas.coords(self.image_id, self.x, self.y)

    def set_image(self, canvas, image_obj):
        """Assign an image to the player and place it on the canvas"""
        self.image = canvas.create_image(self.x, self.y, image=image_obj)
