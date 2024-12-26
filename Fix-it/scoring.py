class Scoring:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.score = 0
        self.x = x
        self.y = y
        self.text_id = self.canvas.create_text(
            self.x, self.y, text=f"Score: {self.score}", font=("Arial", 20),
            fill="black"
            )

    def update_score(self, points):
        self.score += points
        self.canvas.itemconfig(self.text_id, text=f"Score: {self.score}")

    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score
