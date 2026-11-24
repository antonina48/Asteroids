
"""Главное окно игры «Астероиды»."""

import random
import tkinter as tk

import settings as cfg


class Game:
    """Главный класс игры."""

    def __init__(self, root):
        """Создать игровое окно и начальный экран."""
        self.root = root
        self.root.title("Астероиды")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            root,
            width=cfg.WIDTH,
            height=cfg.HEIGHT,
            bg=cfg.BACKGROUND_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack()

        self.lives = cfg.START_LIVES
        self.score = cfg.START_SCORE

        self.draw_background()
        self.draw_hud()
        self.draw_splash()

    def draw_background(self):
        """Нарисовать неподвижный звездный фон."""
        for _ in range(cfg.STAR_COUNT):
            x = random.randint(0, cfg.WIDTH)
            y = random.randint(0, cfg.HEIGHT)
            radius = random.choice([1, 1, 2])

            self.canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill="white",
                outline="",
            )

    def draw_hud(self):
        """Показать количество жизней и очков."""
        self.canvas.create_text(
            20, 20,
            anchor="nw",
            text=f"Lives: {self.lives}",
            fill=cfg.GREEN,
            font=("Arial", 24, "bold"),
        )

        self.canvas.create_text(
            cfg.WIDTH - 20, 20,
            anchor="ne",
            text=f"Score: {self.score}",
            fill=cfg.GREEN,
            font=("Arial", 24, "bold"),
        )

    def draw_splash(self):
        """Нарисовать стартовую заставку."""
        x = cfg.WIDTH / 2
        y = cfg.HEIGHT / 2

        self.canvas.create_rectangle(
            x - cfg.SPLASH_WIDTH / 2,
            y - cfg.SPLASH_HEIGHT / 2,
            x + cfg.SPLASH_WIDTH / 2,
            y + cfg.SPLASH_HEIGHT / 2,
            fill=cfg.SPLASH_COLOR,
            outline=cfg.BLUE,
            width=2,
        )

        self.canvas.create_text(
            x, y - 40,
            text="ASTEROIDS",
            fill=cfg.WHITE,
            font=("Arial", 40, "bold"),
        )

        self.canvas.create_text(
            x, y + 25,
            text="Click to start",
            fill=cfg.GREEN,
            font=("Arial", 22),
        )

        self.canvas.create_text(
            x, y + 75,
            text="Arrows — Move | Space — Shoot",
            fill=cfg.WHITE,
            font=("Arial", 14),
        )


def main():
    """Запустить приложение."""
    root = tk.Tk()
    Game(root)
    root.mainloop()


if __name__ == "__main__":
    main()
