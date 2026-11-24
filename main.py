
"""Главный модуль игры «Астероиды»."""

import random
import time
import tkinter as tk

import settings as cfg
from graphics import Graphics
from models import Asteroid, Explosion, Ship, collides


class Game:
    """Управление игровым процессом и интерфейсом."""

    def __init__(self, root):
        """Создать окно и инициализировать игру."""
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

        self.graphics = Graphics(self.canvas)
        self.keys = set()

        self.ship = Ship(
            cfg.WIDTH / 2, cfg.HEIGHT / 2
        )

        self.asteroids = []
        self.missiles = []
        self.explosions = []

        self.lives = cfg.START_LIVES
        self.score = cfg.START_SCORE

        self.active = False
        self.game_over = False

        self.spawn_timer = 0.0
        self.background_offset = 0.0
        self.last_time = time.perf_counter()

        # Границы стартовой заставки.
        self.splash_left = (
            cfg.WIDTH - cfg.SPLASH_WIDTH
        ) / 2

        self.splash_top = (
            cfg.HEIGHT - cfg.SPLASH_HEIGHT
        ) / 2

        self.splash_right = (
            self.splash_left + cfg.SPLASH_WIDTH
        )

        self.splash_bottom = (
            self.splash_top + cfg.SPLASH_HEIGHT
        )

        # Подключение обработчиков событий.
        root.bind("<KeyPress>", self.on_key_press)
        root.bind("<KeyRelease>", self.on_key_release)
        root.bind("<FocusOut>", self.on_focus_out)

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.focus_set()

        self.loop()

    def start(self):
        """Начать новую игру."""
        self.lives = cfg.START_LIVES
        self.score = cfg.START_SCORE

        self.ship = Ship(
            cfg.WIDTH / 2, cfg.HEIGHT / 2
        )

        self.asteroids.clear()
        self.missiles.clear()
        self.explosions.clear()
        self.keys.clear()

        self.spawn_timer = 0.0
        self.active = True
        self.game_over = False

    def stop(self):
        """Завершить игру, сохранив итоговый счет."""
        self.active = False
        self.game_over = True

        self.asteroids.clear()
        self.missiles.clear()
        self.keys.clear()

    def on_click(self, event):
        """Начать игру при щелчке по заставке."""
        if self.active:
            return

        inside = (
            self.splash_left <= event.x
            <= self.splash_right
            and self.splash_top <= event.y
            <= self.splash_bottom
        )

        if inside:
            self.start()
            self.canvas.focus_set()

    def on_key_press(self, event):
        """Обработать нажатие клавиши."""
        key = event.keysym

        if (
            key == "space"
            and key not in self.keys
            and self.active
        ):
            self.missiles.append(self.ship.fire())

        self.keys.add(key)

    def on_key_release(self, event):
        """Обработать отпускание клавиши."""
        self.keys.discard(event.keysym)

    def on_focus_out(self, event):
        """Сбросить нажатые клавиши при потере фокуса."""
        self.keys.clear()

    def spawn_asteroid(self):
        """Создать астероид в случайном месте."""
        if len(self.asteroids) >= cfg.MAX_ASTEROIDS:
            return

        asteroid = Asteroid(
            random.randrange(cfg.WIDTH),
            random.randrange(cfg.HEIGHT),
        )

        # Не создаем астероид поверх корабля.
        if not collides(asteroid, self.ship):
            self.asteroids.append(asteroid)

    def check_missile_collisions(self):
        """Обработать попадания ракет в астероиды."""
        for missile in self.missiles[:]:
            for asteroid in self.asteroids[:]:

                if collides(missile, asteroid):
                    self.explosions.append(
                        Explosion(asteroid.x, asteroid.y)
                    )

                    self.missiles.remove(missile)
                    self.asteroids.remove(asteroid)

                    self.score += 1
                    break

    def check_ship_collisions(self):
        """Обработать столкновения корабля с астероидами."""
        for asteroid in self.asteroids[:]:

            if collides(self.ship, asteroid):
                self.explosions.append(
                    Explosion(asteroid.x, asteroid.y)
                )

                self.asteroids.remove(asteroid)

                # По заданию игра завершается при смерти,
                # если до столкновения было 0 жизней.
                if self.lives == 0:
                    self.stop()

                else:
                    self.lives -= 1

                    self.ship = Ship(
                        cfg.WIDTH / 2,
                        cfg.HEIGHT / 2,
                    )

                break

    def update(self, dt):
        """Обновить состояние игровых объектов."""
        self.background_offset += (
            cfg.BACKGROUND_SPEED * dt
        )
        self.background_offset %= cfg.WIDTH

        # Обновление тайловой анимации взрывов.
        for explosion in self.explosions:
            explosion.update(dt)

        self.explosions = [
            explosion
            for explosion in self.explosions
            if explosion.is_alive()
        ]

        if not self.active:
            return

        self.ship.update(dt, self.keys)

        # Создание новых астероидов через интервал.
        self.spawn_timer += dt

        while self.spawn_timer >= cfg.ASTEROID_INTERVAL:
            self.spawn_timer -= cfg.ASTEROID_INTERVAL
            self.spawn_asteroid()

        for asteroid in self.asteroids:
            asteroid.update(dt)

        for missile in self.missiles:
            missile.update(dt)

        # Удаление ракет с истекшим временем жизни.
        self.missiles = [
            missile
            for missile in self.missiles
            if missile.is_alive()
        ]

        self.check_missile_collisions()
        self.check_ship_collisions()

    def draw_hud(self):
        """Отобразить количество жизней и очков."""
        self.canvas.create_text(
            20,
            20,
            anchor="nw",
            text=f"Lives: {self.lives}",
            fill=cfg.GREEN,
            font=("Arial", 24, "bold"),
            tags="frame",
        )

        self.canvas.create_text(
            cfg.WIDTH - 20,
            20,
            anchor="ne",
            text=f"Score: {self.score}",
            fill=cfg.GREEN,
            font=("Arial", 24, "bold"),
            tags="frame",
        )

    def draw_splash(self):
        """Нарисовать стартовую заставку."""
        self.canvas.create_rectangle(
            self.splash_left,
            self.splash_top,
            self.splash_right,
            self.splash_bottom,
            fill=cfg.SPLASH_COLOR,
            outline=cfg.BLUE,
            width=2,
            tags="frame",
        )

        self.canvas.create_text(
            cfg.WIDTH / 2,
            cfg.HEIGHT / 2 - 48,
            text="ASTEROIDS",
            fill=cfg.WHITE,
            font=("Arial", 40, "bold"),
            tags="frame",
        )

        if self.game_over:
            message = "GAME OVER — Click to restart"
        else:
            message = "Click to start"

        self.canvas.create_text(
            cfg.WIDTH / 2,
            cfg.HEIGHT / 2 + 20,
            text=message,
            fill=cfg.GREEN,
            font=("Arial", 19),
            tags="frame",
        )

        self.canvas.create_text(
            cfg.WIDTH / 2,
            cfg.HEIGHT / 2 + 70,
            text="Arrows — Move | Space — Shoot",
            fill=cfg.WHITE,
            font=("Arial", 14),
            tags="frame",
        )

    def draw(self):
        """Отрисовать текущий игровой кадр."""
        self.canvas.delete("frame")

        self.graphics.draw_background(
            self.background_offset
        )

        if self.active:
            for asteroid in self.asteroids:
                self.graphics.draw_asteroid(asteroid)

            for missile in self.missiles:
                self.graphics.draw_missile(missile)

            self.graphics.draw_ship(self.ship)

        for explosion in self.explosions:
            self.graphics.draw_explosion(explosion)

        if not self.active:
            self.draw_splash()

        self.draw_hud()

    def loop(self):
        """Обновить кадр и запланировать следующий."""
        current_time = time.perf_counter()

        dt = min(
            current_time - self.last_time,
            cfg.MAX_DT,
        )

        self.last_time = current_time

        self.update(dt)
        self.draw()

        self.root.after(cfg.FRAME_DELAY, self.loop)


def main():
    """Запустить игру."""
    root = tk.Tk()
    Game(root)
    root.mainloop()


if __name__ == "__main__":
    main()
