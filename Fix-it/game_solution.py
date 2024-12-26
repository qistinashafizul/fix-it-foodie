import random
import tkinter as tk
from tkinter import Button, messagebox
from player import Player
from obstacle import Obstacle
from scoring import Scoring
from stall import Stall
from cat import Cat
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, key_bindings
from PIL import Image, ImageTk  # type: ignore
import time

'''DEFINING FUNCTIONS'''


# Define difficulty levels
def set_difficulty(level):
    global selected_difficulty, obstacle_spawn_rate, cat_speed
    selected_difficulty = level
    if level == "Easy":
        obstacle_spawn_rate = 6000
        cat_speed = 30

    elif level == "Medium":
        obstacle_spawn_rate = 4000
        cat_speed = 40

    elif level == "Hard":
        obstacle_spawn_rate = 2000
        cat_speed = 90


# Cheat code detection
def detect_cheat_code(event):
    global cheat_code_input
    cheat_code_input += event.char.upper()
    if cheat_code in cheat_code_input:
        activate_cheat_code()
        cheat_code_input = ""


# Cheat code activation
def activate_cheat_code():
    global player
    player.health += 1  # Give the player extra health
    update_life_images()
    print("Cheat code activated! Extra health granted.")


# boss key function
def toggle_boss_key(event=None):
    global boss_key_active, game_paused, boss_key_window
    if boss_key_active:
        # Hide boss key window and resume the game
        boss_key_window.destroy()
        game_paused = False
        root.after(16, game_loop)  # Resume game loop
    else:
        boss_key_window = tk.Toplevel(root)
        boss_key_window.title("GitLab")
        boss_key_window.geometry(
            f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}"
        )
        boss_key_image = ImageTk.PhotoImage(Image.open
                                            ("assets/working_bg.png"))
        boss_key_label = tk.Label(boss_key_window, image=boss_key_image)
        boss_key_label.image = boss_key_image
        boss_key_label.pack(fill=tk.BOTH, expand=True)
        game_paused = True  # Stop the game loop
    boss_key_active = not boss_key_active


# Stopping the game at the end
def stop_game():
    global game_running
    game_running = False


# Open the settings window
def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")

    tk.Label(settings_window, text="Move Left:").grid(row=0, column=0)
    move_left_entry = tk.Entry(settings_window)
    move_left_entry.grid(row=0, column=1)

    tk.Label(settings_window, text="Move Right:").grid(row=1, column=0)
    move_right_entry = tk.Entry(settings_window)
    move_right_entry.grid(row=1, column=1)

    tk.Label(settings_window, text="Move Up:").grid(row=2, column=0)
    move_up_entry = tk.Entry(settings_window)
    move_up_entry.grid(row=2, column=1)

    tk.Label(settings_window, text="Move Down:").grid(row=3, column=0)
    move_down_entry = tk.Entry(settings_window)
    move_down_entry.grid(row=3, column=1)

    tk.Label(settings_window, text="Difficulty Level:")\
        .grid(row=4, column=0)
    difficulty_var = tk.StringVar(
        value="Easy"
    )
    tk.Radiobutton(settings_window, text="Easy", variable=difficulty_var,
                   value="Easy").grid(row=4, column=1)
    tk.Radiobutton(settings_window, text="Medium", variable=difficulty_var,
                   value="Medium").grid(row=5, column=1)
    tk.Radiobutton(settings_window, text="Hard", variable=difficulty_var,
                   value="Hard").grid(row=6, column=1)

    def save_settings():
        key_bindings['left'] = move_left_entry.get() or 'Left'
        key_bindings['right'] = move_right_entry.get() or 'Right'
        key_bindings['up'] = move_up_entry.get() or 'Up'
        key_bindings['down'] = move_down_entry.get() or 'Down'
        selected_difficulty = difficulty_var.get()
        set_difficulty(selected_difficulty)
        settings_window.destroy()
    tk.Button(settings_window, text="Save Settings",
              command=save_settings).grid(row=7, column=0, columnspan=2)


# Resizing background when reconfigured
def resize_bg(event=None):
    # Get the new window size
    window_width = root.winfo_width()
    window_height = root.winfo_height()

    # Resize the game background image
    resized_bg = game_bg.resize(
        (window_width, window_height), Image.Resampling.LANCZOS
    )
    bg_image = ImageTk.PhotoImage(resized_bg)
    background_images['game'] = bg_image

    # Resize the intro background image
    resized_intro_bg = intro_bg_original.resize((window_width, window_height),
                                                Image.Resampling.LANCZOS)
    intro_bg_image = ImageTk.PhotoImage(resized_intro_bg)
    background_images['intro'] = intro_bg_image

    # Update the canvases with resized backgrounds
    game_canvas.create_image(0, 0, anchor=tk.NW, image=bg_image)
    game_canvas.image = bg_image

    intro_canvas.create_image(0, 0, anchor=tk.NW, image=intro_bg_image)
    intro_canvas.image = intro_bg_image


# Check for collision between two bounding boxes
def check_collision(box1, box2):
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2

    return not (x1_max < x2_min or x1_min > x2_max
                or y1_max < y2_min or y1_min > y2_max)


# Check for collision between the cat and the stalls
def check_cat_stall_collision(cat, stalls):
    cat_box = cat.get_position()
    for stall in stalls:
        stall_box = stall.get_position()
        if check_collision(cat_box, stall_box):
            stall.make_unfixed()


# Spawning the fruits
def spawn_obstacle():
    global PLATFORMS, fruit_img, game_paused, obstacle_spawn_rate
    if not game_paused:
        fruit_image = random.choice(fruit_img)
        obstacle = Obstacle(game_canvas, x=1200, y=PLATFORMS[0],
                            image_path=fruit_image, platforms=PLATFORMS)
        obstacles.append(obstacle)
        root.after(obstacle_spawn_rate, spawn_obstacle)


# Moving the obstacles
def move_obstacles():
    global game_paused
    if not game_paused:
        for obstacle in obstacles[:]:
            if not obstacle.move():
                obstacles.remove(obstacle)


# Check for collision between the player and the obstacles
def check_player_obstacle_collision(player, obstacles):
    player_box = player.get_position()
    for obstacle in obstacles:
        obstacle_box = obstacle.get_position()
        if check_collision(player_box, obstacle_box):
            player.health -= 1
            update_life_images()
            obstacle.delete()
            obstacles.remove(obstacle)
            game_canvas.delete(obstacle.image_id)
            if player.health <= 0:
                print("Game Over")
                stop_game()
                show_game_over()


# Update the life images when reduced
def update_life_images():
    global life_images, player, game_canvas, life_image
    # Clear existing life images
    for img in life_images:
        game_canvas.delete(img)
    life_images = []

    # Add life images based on player's health
    for i in range(player.health):
        img = game_canvas.create_image(900 + i * 40, 0,
                                       anchor="nw", image=life_image)
        life_images.append(img)


# Load the objects at start of the game
def load_obj():
    global game_paused, player, stalls, cat, scoring
    global obstacles, life_image, life_images
    if not game_paused:
        #  Load stalls
        stall1 = Stall(game_canvas, x=140, y=80,
                       fixed_img="assets/NLStand_fix.png",
                       unfixed_img="assets/NLStand.png",
                       points=10)
        stall2 = Stall(game_canvas, x=1200, y=320,
                       fixed_img="assets/RCStand_fix.png",
                       unfixed_img="assets/RCStand.png",
                       points=50)
        stall3 = Stall(game_canvas, x=140, y=570,
                       fixed_img="assets/TTStall_fix.png",
                       unfixed_img="assets/TTStall.png",
                       points=10)
        fruit = Stall(game_canvas, x=1200, y=80,
                      fixed_img="assets/FMachine.png",
                      unfixed_img="assets/FMachine.png",
                      points=0)

        stalls = [stall1, stall2, stall3, fruit]

        stall_images.extend([stall1.current_img, stall2.current_img,
                             stall3.current_img, fruit.current_img])
        # Initialize scoring
        scoring = Scoring(game_canvas, x=1190, y=35)
        player = Player(game_canvas, 200, 400,
                        idle_sprite_path="assets/John/Idle.png",
                        run_sprite_sheet_path_right="assets/John/Run_R.png",
                        run_sprite_sheet_path_left="assets/John/Run_L.png",
                        scoring=scoring)
        cat = Cat(game_canvas, 500, 400,
                  calico_right="assets/Calico/Run_R.png",
                  calico_left="assets/Calico/Run_L.png",
                  pause_state=lambda: game_paused,
                  speed=cat_speed)

        life_image = ImageTk.PhotoImage(
            Image.open("assets/lives.png").resize((192, 108),
                                                  Image.Resampling.LANCZOS)
            )
        life_images = [game_canvas.create_image(
                       900 + i * 40, 0, anchor="nw",
                       image=life_image) for i in range(player.health)]
        spawn_obstacle()


# Check if there is saved data and apply it
def check_loaded():
    global loaded_data, player, scoring, key_bindings
    if loaded_data:
        try:
            # Extract player data
            player_x, player_y, player_health = loaded_data["player"]

            # Extract score
            score = loaded_data["score"]

            # Extract key bindings
            key_bindings = loaded_data["key_bindings"]

            # Apply loaded data to the player object
            player.x = player_x
            player.y = player_y
            player.health = player_health
            player.update()  # Update visual representation, if applicable

            # Apply the loaded score
            scoring.set_score(score)
            scoring.update_score(0)  # Update score display

            print("Game loaded successfully!")
        except Exception as e:
            print(f"Error applying loaded data: {e}")
    else:
        print("No saved data provided. Starting a new game.")


# Start the game
def start_game(event=None):
    global player, stalls, cat, scoring, obstacles, life_image, life_images
    global player_name, game_running, game_paused, start_time, loaded_data
    global key_bindings

    player_name = name_entry.get()
    intro_canvas.place_forget()
    start_btn.place_forget()
    name_entry.place_forget()
    name_label.place_forget()

    game_canvas.place(x=0, y=0, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    resize_bg()

    game_running = True
    game_paused = False

    start_time = time.time()
    game_canvas.delete("all")
    stalls.clear()
    obstacles.clear()
    life_images.clear()
    game_canvas.create_image(0, 0, anchor="nw", image=background_images['game']
                             )
    game_canvas.after(10, load_obj)
    game_canvas.after(11, check_loaded)
    game_canvas.after(20, game_loop)


# Main movement of John (player)
def move_player(event):
    global game_paused, key_bindings
    if not game_paused:
        if event.keysym == key_bindings['left']:
            player.move_left()
        elif event.keysym == key_bindings['right']:
            player.move_right()
        elif event.keysym == key_bindings['up']:
            player.move_up()
        elif event.keysym == key_bindings['down']:
            player.move_down()
        elif event.keysym == "f":
            player.interact_stall(stalls)
        elif event.keysym == "space":
            player.jump()


# Stop the player movement when key is released
def stop_player(event):
    global player, game_paused
    if player and not game_paused:
        player.stop_running()


def save_game(player_name):
    try:
        # Read existing data from the save file
        save_data = {}
        try:
            with open("savegame.txt", "r") as file:
                for line in file:
                    if line.startswith("Name:"):
                        current_name = line.strip().split(":")[1]
                        save_data[current_name] = []
                    elif current_name:
                        save_data[current_name].append(line.strip())
        except FileNotFoundError:
            pass  # File doesn't exist yet, no data to read

        # Update or add the current player's data
        save_data[player_name] = [
            f"{player.x},{player.y},{player.health}",
            f"{scoring.get_score()}",
            *[f"{key}:{value}" for key, value in key_bindings.items()]
        ]

        # Write all data back to the file
        with open("savegame.txt", "w") as file:
            for name, data in save_data.items():
                file.write(f"Name:{name}\n")
                file.writelines(f"{line}\n" for line in data)

        messagebox.showinfo(
            "Save Game",
            f"Game saved successfully for {player_name}!"
        )
    except Exception as e:
        messagebox.showerror("Save Game", f"Error saving game: {e}")


def load_game(player_name):
    global loaded_data
    try:
        with open("savegame.txt", "r") as file:
            save_data = {}
            current_name = None

            # Parse the save file
            for line in file:
                if line.startswith("Name:"):
                    current_name = line.strip().split(":")[1]
                    save_data[current_name] = []
                elif current_name:
                    save_data[current_name].append(line.strip())

            # Check if the player's name exists
            if player_name in save_data:
                player_data = save_data[
                    player_name
                ]

                # Extract player data
                player_x, player_y, player_health = map(
                    int, player_data[0].split(",")
                )
                score = int(player_data[1])
                key_bindings = {
                    key: value
                    for key, value in (
                        line.split(":") for line in player_data[2:]
                    )
                }

                # Store data in a structured format
                loaded_data = {
                    "name": player_name,
                    "player": (player_x, player_y, player_health),
                    "score": score,
                    "key_bindings": key_bindings,
                }

                messagebox.showinfo(
                    "Load Game",
                    f"Game loaded successfully for {player_name}!"
                )
            else:
                messagebox.showerror(
                    "Load Game", f"No save found for player: {player_name}"
                )

    except FileNotFoundError:
        messagebox.showerror("Load Game", "No save game found.")
    except Exception as e:
        messagebox.showerror("Load Game", f"Error loading game: {e}")


# Function to show the pause pop-up
def show_pause_window():
    global pause_window

    pause_window = tk.Toplevel(root)  # Create a new window
    pause_window.title("Game Paused")  # Set the window title
    pause_window.geometry("200x150")  # Set the window size

    resume_label = tk.Label(pause_window, text="Press 'P' to unpause")
    resume_label.pack(pady=10)

    save_button = tk.Button(
        pause_window, text="Save Game", command=lambda: save_game(player_name)
    )
    save_button.pack(pady=10)

    quit_button = tk.Button(pause_window, text="Quit", command=root.quit)
    quit_button.pack(pady=10)

    pause_window.grab_set()


# Pause the game
def pause_game():
    global game_paused, pause_start
    game_paused = True
    pause_start = time.time()
    show_pause_window()


# Resume the game
def resume_game():
    global game_paused, pause_window, pause_start, pause_time
    pause_end = time.time()
    if pause_time > 0:
        current_pause_time = pause_end - pause_start
        pause_time += current_pause_time
    else:
        current_pause_time = pause_end - pause_start
        pause_time = current_pause_time
    game_paused = False
    if pause_window:
        pause_window.destroy()  # Destroy the pause window
    game_loop()   # Resume game loop


# Toggle when P is pressed
def toggle_pause():
    global game_paused
    if game_paused:
        resume_game()
    else:
        pause_game()


# Move to game over window
def show_game_over():
    global player_name, scoring, start_time, pause_time
    game_canvas.place_forget()  # Hide the game canvas

    # Create the game over screen
    game_over_screen = tk.Frame(root, bg="black")
    game_over_screen.place(x=0, y=0, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)

    end_time = time.time()
    total_time = (end_time - start_time) - pause_time

    # Adjust the score based on the total time
    adjusted_score = scoring.get_score() / total_time

    # Title
    tk.Label(
        game_over_screen,
        text="GAME OVER",
        font=("Courier New", 48, "bold"),  # Monospace font
        fg="#FF6347",  # Tomato red color
        bg="black"
    ).place(relx=0.5, y=50, anchor="center")

    # Score and Time
    tk.Label(
        game_over_screen,
        text=f"Your Score: {scoring.get_score()}",
        font=("Courier New", 24),
        fg="white",
        bg="black"
    ).place(relx=0.5, y=150, anchor="center")

    tk.Label(
        game_over_screen,
        text=f"Total Time: {total_time:.2f} seconds",
        font=("Courier New", 24),
        fg="white",
        bg="black"
    ).place(relx=0.5, y=200, anchor="center")

    # Leaderboard Title
    tk.Label(
        game_over_screen,
        text="LEADERBOARD",
        font=("Courier New", 28, "underline"),
        fg="#FFD700",  # Gold color
        bg="black"
    ).place(relx=0.2, y=300, anchor="center")

    # Load and Display Leaderboard
    try:
        with open("leaderboard.txt", "r") as file:
            leaderboard = [line.strip().split(",") for line in file.readlines()
                           ]
    except FileNotFoundError:
        leaderboard = []

    # Update or add the player entry based on the current score
    player_entry = [player_name, f"{scoring.get_score():.2f}",
                    f"{total_time:.2f}", f"{adjusted_score:.2f}"]

    # Check if the player already exists in the leaderboard
    updated = False
    for entry in leaderboard:
        if len(entry) >= 4:  # Ensure entry has enough elements
            if entry[0] == player_name:
                if float(entry[3]) < float(player_entry[3]):
                    entry[1], entry[2], entry[3] = (
                        player_entry[1],
                        player_entry[2],
                        player_entry[3]
                    )
                updated = True
                break

    # If the player isn't on the leaderboard, add them
    if not updated:
        leaderboard.append(player_entry)

    # Sort leaderboard by adjusted score (index 3) in descending order
    leaderboard.sort(key=lambda x: float(x[3]), reverse=True)

    # Keep only the top 10 players
    leaderboard = leaderboard[:10]

    # Leaderboard Entries
    leaderboard_frame = tk.Frame(game_over_screen, bg="black")
    leaderboard_frame.place(relx=0.3, y=350, anchor="n")

    for rank, entry in enumerate(leaderboard, start=1):
        tk.Label(
            leaderboard_frame,
            text=f"{rank}. {entry[0]}: {entry[1]} points in "
                 f"{entry[2]} seconds",
            font=("Courier New", 18),
            fg="white",
            bg="black"
        ).pack(anchor="w", pady=2)

    # Save the updated leaderboard to file
    with open("leaderboard.txt", "w") as file:
        for entry in leaderboard:
            file.write(f"{entry[0]},{entry[1]},{entry[2]},{entry[3]}\n")

    # Buttons
    tk.Button(
        game_over_screen,
        text="PLAY AGAIN",
        command=lambda: restart_game(),
        font=("Courier New", 20, "bold"),
        bg="#32CD32",  # Lime green
        fg="black",
        activebackground="white",
        activeforeground="black"
    ).place(relx=0.6, y=500, anchor="center")

    tk.Button(
        game_over_screen,
        text="QUIT",
        command=root.quit,
        font=("Courier New", 20, "bold"),
        bg="#FF4500",  # Orange red
        fg="black",
        activebackground="white",
        activeforeground="black"
    ).place(relx=0.6, y=570, anchor="center")

    def restart_game():
        game_over_screen.place_forget()
        name_entry.delete(0, tk.END)
        name_entry.insert(0, player_name)
        start_game()
        name_entry.focus()


def show_leaderboard():
    try:
        with open('leaderboard.txt', 'r') as file:
            leaderboard = [
                line.strip().split(',') for line in file.readlines()
            ]

        # Create a pop-up window
        root = tk.Tk()
        root.title("Leaderboard")
        root.geometry("400x400")
        root.configure(bg="black")

        leaderboard_frame = tk.Frame(root, bg="black")
        leaderboard_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            leaderboard_frame,
            text="Leaderboard",
            font=("Courier New", 24),
            fg="white",
            bg="black"
        ).pack(anchor="n", pady=10)

        for rank, entry in enumerate(leaderboard, start=1):
            tk.Label(
                leaderboard_frame,
                text=f"{rank}. {entry[0]}: {entry[1]} points in "
                     f"{entry[2]} seconds",
                font=("Courier New", 18),
                fg="white",
                bg="black"
            ).pack(anchor="w", pady=2)
        root.mainloop()
    except FileNotFoundError:
        print("Leaderboard file not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Main game loop
def game_loop():

    if game_running and not game_paused:
        global cat, stalls, obstacles
        check_cat_stall_collision(cat, stalls)
        check_player_obstacle_collision(player, obstacles)
        move_obstacles()
        root.after(16, game_loop)


'''START OF EXECUTION OF CODE'''


# Main game window setup
root = tk.Tk()
root.title("Fix-it Foodie")
root.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}")

background_images = {}
stall_images = []
stalls = []
obstacles = []
life_image = []
life_images = []
fruit_img = [
    "assets/Fruits/lemon.png",
    "assets/Fruits/Banana.png",
    "assets/Fruits/Mango.png",
    "assets/Fruits/coco.png",
    "assets/Fruits/Cereza.png",
    "assets/Fruits/Manzana.png",
    "assets/Fruits/melocoton.png",
    "assets/Fruits/Pera.png",
    "assets/Fruits/mora.png",
    "assets/Fruits/Orange.png",
    "assets/Fruits/Pinneaple.png",
    "assets/Fruits/sandia.png",
    "assets/Fruits/Strawberry.png",
    "assets/Fruits/Uva.png"
]

start_time = None
PLATFORMS = [250, 500, 700]
game_running = True
game_paused = False
boss_key_active = False
selected_difficulty = "Easy"
obstacle_spawn_rate = 10000
cat_speed = 30
loaded_data = None
pause_time = 0


# Cheat code detection
cheat_code = "QSIA"
cheat_code_input = ""

# Load background images as PIL Images for resizing
intro_bg_original = Image.open("assets/intro_bg.png")
game_bg = Image.open("assets/background.png")

SCREEN_WIDTH = root.winfo_screenwidth()
SCREEN_HEIGHT = root.winfo_screenheight()

# Intro canvas
intro_canvas = tk.Canvas(
    root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT
)
intro_bg_resized = ImageTk.PhotoImage(
    intro_bg_original.resize((SCREEN_WIDTH, SCREEN_HEIGHT),
                             Image.Resampling.LANCZOS)
)
intro_canvas.create_image(0, 0,
                          anchor="nw", image=intro_bg_resized)
intro_canvas.place(x=0, y=0, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)

# Create the boss key screen
boss_key_canvas = tk.Canvas(root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
boss_key_image = ImageTk.PhotoImage(Image.open("assets/working_bg.png"))
boss_key_canvas.create_image(0, 0, anchor="nw", image=boss_key_image)

# Initially hide the boss key screen
boss_key_canvas.pack_forget()

# Create the pause screen
pause_canvas = tk.Canvas(root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
pause_canvas.create_text(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                         text="Game Paused", font=("Arial", 24), fill="white")
save_button = tk.Button(root, text="Save Game", command=save_game)
pause_canvas.create_window(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                           window=save_button)

# Initially hide the pause screen
pause_canvas.pack_forget()

# Updated colors and font style to match your theme
retro_font = ("Press Start 2P", 16)  # pixel-style font or similar retro font

# Create a frame for grouping the label and entry
input_frame = tk.Frame(root, bg="#1E1E3F", bd=3, relief="ridge")
input_frame.place(relx=0.75, rely=0.25, anchor="center")

# Add the label with purple text and retro font
name_label = tk.Label(
    input_frame,
    text="ENTER YOUR NAME:",
    font=retro_font,
    bg="#1E1E3F",
    fg="#D8BFD8"
)
name_label.pack(pady=10)

# Add the entry field with a matching border and retro styling
name_entry = tk.Entry(
    input_frame,
    font=retro_font,
    width=20,
    bg="#FF6347",
    fg="#FFFFFF",
    bd=5,
    relief="ridge",
    insertbackground="#FFFFFF"  # White cursor
)
name_entry.pack(pady=10)

start = Image.open("assets/start_btn.png").convert("RGBA")
start_img = ImageTk.PhotoImage(start)
start_btn = Button(root, image=start_img, command=start_game, borderwidth=0,
                   highlightthickness=0)
start_btn.place(x=SCREEN_WIDTH//2-500, y=SCREEN_HEIGHT//2+100)

# Styling variables
BUTTON_WIDTH = 20
BUTTON_HEIGHT = 2
BUTTON_BG = "#FF4500"
BUTTON_FG = "white"
BUTTON_FONT = ("Press Start2P", 16)
BUTTON_SPACING = 10

# Create a frame for buttons
button_frame = tk.Frame(root, bg="#1E1E3F")  # Match background color
button_frame.place(relx=0.75, rely=0.6, anchor="center")  # Center the frame

# Add buttons to the frame
settings_button = tk.Button(
    button_frame, text="SETTINGS", width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
    bg=BUTTON_BG, fg=BUTTON_FG, font=BUTTON_FONT, command=open_settings
)
settings_button.pack(pady=BUTTON_SPACING)

load_btn = tk.Button(
    button_frame, text="LOAD GAME", width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
    bg=BUTTON_BG, fg=BUTTON_FG, font=BUTTON_FONT, command=lambda: load_game(
        name_entry.get())
)
load_btn.pack(pady=BUTTON_SPACING)

tutorial_btn = tk.Button(
    button_frame, text="TUTORIAL", width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
    bg=BUTTON_BG, fg=BUTTON_FG, font=BUTTON_FONT,
    command=lambda: messagebox.showinfo(
        "Tutorial",
        "Use the arrow keys to move John around the screen. "
        "Fix stalls(f) to earn points. "
        "Dodge the fruits by jumping (space bar) or moving to different"
        "platforms. Oh and don't worry, you can hit the cat!"
    )
)
tutorial_btn.pack(pady=BUTTON_SPACING)


leaderboard_button = tk.Button(
    button_frame, text="LEADERBOARD", width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
    bg=BUTTON_BG, fg=BUTTON_FG, font=BUTTON_FONT, command=show_leaderboard
)
leaderboard_button.pack(pady=BUTTON_SPACING)

exit_button = tk.Button(
    button_frame, text="EXIT", width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
    bg=BUTTON_BG, fg=BUTTON_FG, font=BUTTON_FONT, command=root.quit
)
exit_button.pack(pady=BUTTON_SPACING)

# Game canvas
game_canvas = tk.Canvas(root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)


root.bind("<KeyPress>", move_player)
root.bind("<KeyRelease>", stop_player)
root.bind("<KeyPress-p>", lambda event: toggle_pause())
root.bind("<b>", toggle_boss_key)
root.bind_all("<KeyPress>", detect_cheat_code)
root.focus_set()

root.mainloop()
