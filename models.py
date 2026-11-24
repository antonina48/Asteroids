
"""Модели игровых объектов."""

import math
import random

import settings as cfg


def direction(angle):
    """Вычислить направление движения по углу."""
    radians = math.radians(angle)
    return math.cos(radians), math.sin(radians)


def collides(first, second):
    """Проверить столкновение двух объектов."""
    dx = abs(first.x - second.x)
    dy = abs(first.y - second.y)

    # Учитываем тороидальную геометрию поля.
    dx = min(dx, cfg.WIDTH - dx)
    dy = min(dy, cfg.HEIGHT - dy)

    radius = first.radius + second.radius

    return dx ** 2 + dy ** 2 <= radius ** 2


class Body:
    """Базовый класс движущегося объекта."""

    def __init__(self, x, y, radius):
        """Задать начальные параметры объекта."""
        self.x = x
        self.y = y
        self.radius = radius

        self.vx = 0.0
        self.vy = 0.0

        self.angle = 0.0
        self.angular_velocity = 0.0

    def move(self, dt):
        """Обновить координаты и угол поворота."""
        self.x += self.vx * dt
        self.y += self.vy * dt

        self.angle += self.angular_velocity * dt
        self.angle %= 360

        # Переход через противоположные границы поля.
        self.x %= cfg.WIDTH
        self.y %= cfg.HEIGHT


class Ship(Body):
    """Космический корабль игрока."""

    def __init__(self, x, y):
        """Создать неподвижный корабль."""
        super().__init__(x, y, cfg.SHIP_RADIUS)
        self.thrust = False

    def update(self, dt, keys):
        """Обработать управление и движение корабля."""
        rotation = 0

        if "Left" in keys:
            rotation -= cfg.SHIP_ROTATION_SPEED

        if "Right" in keys:
            rotation += cfg.SHIP_ROTATION_SPEED

        self.angular_velocity = rotation
        self.thrust = "Up" in keys

        if self.thrust:
            angle = self.angle + rotation * dt
            dx, dy = direction(angle)

            self.vx += dx * cfg.SHIP_ACCELERATION * dt
            self.vy += dy * cfg.SHIP_ACCELERATION * dt

            speed = math.hypot(self.vx, self.vy)

            # Ограничиваем максимальную скорость.
            if speed > cfg.SHIP_MAX_SPEED:
                factor = cfg.SHIP_MAX_SPEED / speed
                self.vx *= factor
                self.vy *= factor

        else:
            speed = math.hypot(self.vx, self.vy)

            # Постепенное торможение корабля.
            new_speed = max(
                0, speed - cfg.SHIP_BRAKING * dt
            )

            if new_speed == 0:
                self.vx = 0
                self.vy = 0
            else:
                factor = new_speed / speed
                self.vx *= factor
                self.vy *= factor

        self.move(dt)

    def fire(self):
        """Создать ракету в носовой части корабля."""
        dx, dy = direction(self.angle)

        x = (self.x + dx * cfg.SHIP_NOSE) % cfg.WIDTH
        y = (self.y + dy * cfg.SHIP_NOSE) % cfg.HEIGHT

        return Missile(x, y, self.angle)


class Asteroid(Body):
    """Астероид со случайной скоростью движения."""

    def __init__(self, x, y):
        """Создать астероид со случайными параметрами."""
        super().__init__(x, y, cfg.ASTEROID_RADIUS)

        self.angle = random.uniform(0, 360)

        movement_angle = random.uniform(0, 360)
        dx, dy = direction(movement_angle)

        speed = random.uniform(
            cfg.ASTEROID_MIN_SPEED,
            cfg.ASTEROID_MAX_SPEED,
        )

        self.vx = dx * speed
        self.vy = dy * speed

        self.angular_velocity = random.uniform(
            -cfg.ASTEROID_MAX_ROTATION,
            cfg.ASTEROID_MAX_ROTATION,
        )

    def update(self, dt):
        """Обновить положение астероида."""
        self.move(dt)


class Missile(Body):
    """Ракета с ограниченным временем жизни."""

    def __init__(self, x, y, angle):
        """Задать направление и скорость ракеты."""
        super().__init__(x, y, cfg.MISSILE_RADIUS)

        self.angle = angle
        dx, dy = direction(angle)

        self.vx = dx * cfg.MISSILE_SPEED
        self.vy = dy * cfg.MISSILE_SPEED

        self.age = 0.0

    def update(self, dt):
        """Переместить ракету и увеличить ее возраст."""
        self.move(dt)
        self.age += dt

    def is_alive(self):
        """Проверить время жизни ракеты."""
        return self.age < cfg.MISSILE_LIFETIME


class Explosion:
    """Модель тайловой анимации взрыва."""

    def __init__(self, x, y):
        """Задать координаты взрыва."""
        self.x = x
        self.y = y
        self.age = 0.0

    def update(self, dt):
        """Обновить время анимации."""
        self.age += dt

    def frame(self):
        """Определить номер текущего кадра."""
        return int(self.age / cfg.EXPLOSION_FRAME_TIME)

    def is_alive(self):
        """Проверить, завершилась ли анимация."""
        return self.frame() < cfg.EXPLOSION_FRAMES
