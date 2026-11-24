
"""Графические ресурсы и отрисовка игровых объектов."""

import base64
import math
import random
import struct
import tkinter as tk
import zlib

import settings as cfg


TRANSPARENT = (0, 0, 0, 0)


def png_chunk(name, data):
    """Сформировать блок данных изображения PNG."""
    checksum = zlib.crc32(name + data) & 0xffffffff

    return (
        struct.pack(">I", len(data))
        + name
        + data
        + struct.pack(">I", checksum)
    )


def make_image(master, width, height, pixel):
    """Создать изображение с поддержкой прозрачности."""
    raw = bytearray()

    for y in range(height):
        raw.append(0)

        for x in range(width):
            raw.extend(pixel(x, y))

    header = struct.pack(
        ">IIBBBBB", width, height, 8, 6, 0, 0, 0
    )

    png = (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", header)
        + png_chunk(b"IDAT", zlib.compress(bytes(raw)))
        + png_chunk(b"IEND", b"")
    )

    return tk.PhotoImage(
        master=master,
        data=base64.b64encode(png).decode("ascii"),
        format="png",
    )


def inside_polygon(x, y, points):
    """Проверить принадлежность точки многоугольнику."""
    inside = False

    for first, second in zip(
        points, points[1:] + points[:1]
    ):
        x1, y1 = first
        x2, y2 = second

        if (y1 > y) != (y2 > y):
            boundary = (
                (x2 - x1) * (y - y1) / (y2 - y1) + x1
            )

            if x < boundary:
                inside = not inside

    return inside


def ship_pixel(x, y, thrust):
    """Определить цвет пикселя корабля."""
    body = ((29, 0), (-16, -21), (-6, 0), (-16, 21))
    flame = ((-28, 0), (-7, -8), (-7, 8))

    # Кабина корабля.
    if (x - 8) ** 2 + y ** 2 * 2 < 36:
        return 65, 200, 255, 255

    # Основной корпус.
    if inside_polygon(x, y, body):
        return 180, 205, 235, 255

    # Пламя работающего двигателя.
    if thrust and inside_polygon(x, y, flame):
        return 255, 130, 35, 255

    return TRANSPARENT


def rock_pixel(x, y):
    """Определить цвет пикселя астероида."""
    angle = math.atan2(y, x)
    distance = math.hypot(x, y)

    # Формируем неровную поверхность астероида.
    radius = (
        30
        + 3 * math.sin(5 * angle)
        + 2 * math.cos(7 * angle)
    )

    if distance > radius:
        return TRANSPARENT

    craters = (
        (-12, -10, 7),
        (13, 6, 8),
        (-6, 14, 5),
        (10, -15, 4),
    )

    for cx, cy, crater_radius in craters:
        if (
            (x - cx) ** 2 + (y - cy) ** 2
            < crater_radius ** 2
        ):
            return 65, 70, 85, 255

    if distance > radius - 2:
        return 180, 185, 195, 255

    return 115, 120, 140, 255


def missile_pixel(x, y):
    """Определить цвет пикселя ракеты."""
    if (x / 8) ** 2 + (y / 3) ** 2 <= 1:
        return 255, 230, 110, 255

    return TRANSPARENT


def rotated_image(master, size, angle, pixel):
    """Создать повернутое изображение объекта."""
    radians = math.radians(angle)
    cosine = math.cos(radians)
    sine = math.sin(radians)

    center = (size - 1) / 2

    def rotated_pixel(x, y):
        """Преобразовать координаты при повороте."""
        dx = x - center
        dy = y - center

        local_x = dx * cosine + dy * sine
        local_y = -dx * sine + dy * cosine

        return pixel(local_x, local_y)

    return make_image(master, size, size, rotated_pixel)


def make_explosion_frames(master):
    """Создать лист тайлов и кадры анимации взрыва."""
    size = cfg.EXPLOSION_SIZE
    count = cfg.EXPLOSION_FRAMES

    def explosion_pixel(x, y):
        """Определить цвет пикселя кадра взрыва."""
        frame = x // size
        progress = frame / (count - 1)

        local_x = x % size - size / 2
        local_y = y - size / 2

        distance = math.hypot(local_x, local_y)
        radius = 6 + 36 * progress
        alpha = int(255 * (1 - progress))

        if distance < radius * 0.4:
            return 255, 245, 160, alpha

        if distance < radius * 0.75:
            return 255, 165, 30, alpha

        if distance < radius:
            return 255, 65, 15, alpha

        return TRANSPARENT

    # Создаем единое изображение со всеми кадрами.
    sheet = make_image(
        master, size * count, size, explosion_pixel
    )

    frames = []

    # Извлекаем отдельные тайлы из изображения.
    for index in range(count):
        frame = tk.PhotoImage(
            master=master,
            width=size,
            height=size,
        )

        frame.tk.call(
            str(frame),
            "copy",
            str(sheet),
            "-from",
            index * size,
            0,
            (index + 1) * size,
            size,
        )

        frames.append(frame)

    return sheet, frames


class Graphics:
    """Управление графическими ресурсами игры."""

    def __init__(self, canvas):
        """Создать фон и подготовить изображения."""
        self.canvas = canvas
        self.cache = {}

        self.sheet, self.explosion_frames = (
            make_explosion_frames(canvas)
        )

        rng = random.Random(42)

        # Неподвижный звездный фон.
        for _ in range(cfg.STAR_COUNT):
            x = rng.randrange(cfg.WIDTH)
            y = rng.randrange(cfg.HEIGHT)
            radius = rng.choice((1, 1, 1, 2))

            self.canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill=rng.choice(
                    ("#ffffff", "#98afd8", "#536a9c")
                ),
                outline="",
                tags="stars",
            )

        # Координаты фоновых астероидов.
        self.rock_positions = [
            (
                rng.randrange(cfg.WIDTH),
                rng.randrange(cfg.HEIGHT),
            )
            for _ in range(cfg.BACKGROUND_ROCK_COUNT)
        ]

        size = cfg.BACKGROUND_ROCK_SIZE

        def background_pixel(x, y):
            """Создать полупрозрачный фоновый астероид."""
            scale = cfg.ASTEROID_IMAGE_SIZE / size

            red, green, blue, alpha = rock_pixel(
                (x - size / 2) * scale,
                (y - size / 2) * scale,
            )

            alpha = alpha * cfg.BACKGROUND_ALPHA // 255

            return red, green, blue, alpha

        self.background_rock = make_image(
            canvas, size, size, background_pixel
        )

    def sprite(self, kind, angle, thrust=False):
        """Получить изображение нужной ориентации."""
        angle = (
            round(angle / cfg.ANGLE_STEP) * cfg.ANGLE_STEP
        ) % 360

        key = kind, angle, thrust

        if key not in self.cache:
            if kind == "ship":
                size = cfg.SHIP_IMAGE_SIZE

                def pixel(x, y):
                    """Выбрать состояние двигателя."""
                    return ship_pixel(x, y, thrust)

            elif kind == "asteroid":
                size = cfg.ASTEROID_IMAGE_SIZE
                pixel = rock_pixel

            else:
                size = cfg.MISSILE_IMAGE_SIZE
                pixel = missile_pixel

            self.cache[key] = rotated_image(
                self.canvas, size, angle, pixel
            )

        return self.cache[key]

    def draw_wrapped(self, image, x, y):
        """Отобразить объект с учетом границ поля."""
        for dx in (-cfg.WIDTH, 0, cfg.WIDTH):
            for dy in (-cfg.HEIGHT, 0, cfg.HEIGHT):
                px = x + dx
                py = y + dy

                half_width = image.width() / 2
                half_height = image.height() / 2

                if (
                    -half_width <= px
                    <= cfg.WIDTH + half_width
                    and -half_height <= py
                    <= cfg.HEIGHT + half_height
                ):
                    self.canvas.create_image(
                        px,
                        py,
                        image=image,
                        tags="frame",
                    )

    def draw_background(self, offset):
        """Нарисовать движущийся полупрозрачный фон."""
        for x, y in self.rock_positions:
            position = (x - offset) % cfg.WIDTH

            self.draw_wrapped(
                self.background_rock, position, y
            )

    def draw_ship(self, ship):
        """Нарисовать космический корабль."""
        image = self.sprite(
            "ship", ship.angle, ship.thrust
        )

        self.draw_wrapped(image, ship.x, ship.y)

    def draw_asteroid(self, asteroid):
        """Нарисовать вращающийся астероид."""
        image = self.sprite("asteroid", asteroid.angle)

        self.draw_wrapped(image, asteroid.x, asteroid.y)

    def draw_missile(self, missile):
        """Нарисовать летящую ракету."""
        image = self.sprite("missile", missile.angle)

        self.draw_wrapped(image, missile.x, missile.y)

    def draw_explosion(self, explosion):
        """Нарисовать текущий кадр взрыва."""
        if explosion.is_alive():
            image = self.explosion_frames[explosion.frame()]

            self.draw_wrapped(
                image, explosion.x, explosion.y
            )
