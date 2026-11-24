
"""Основные параметры игры «Астероиды»."""

# Размеры игрового поля.
WIDTH = 900
HEIGHT = 600

# Интервал обновления экрана в миллисекундах.
FRAME_DELAY = 16
MAX_DT = 0.05

# Начальное количество жизней и очков.
START_LIVES = 3
START_SCORE = 0

# Параметры корабля.
SHIP_RADIUS = 20
SHIP_ACCELERATION = 260
SHIP_MAX_SPEED = 320
SHIP_ROTATION_SPEED = 210
SHIP_BRAKING = 90
SHIP_NOSE = 29

# Параметры астероидов.
ASTEROID_RADIUS = 32
ASTEROID_MIN_SPEED = 45
ASTEROID_MAX_SPEED = 115
ASTEROID_MAX_ROTATION = 100
ASTEROID_INTERVAL = 1.2
MAX_ASTEROIDS = 15

# Параметры ракет.
MISSILE_RADIUS = 4
MISSILE_SPEED = 480
MISSILE_LIFETIME = 0.9

# Параметры тайловой анимации взрыва.
EXPLOSION_SIZE = 96
EXPLOSION_FRAMES = 12
EXPLOSION_FRAME_TIME = 0.045

# Размеры изображений игровых объектов.
SHIP_IMAGE_SIZE = 64
ASTEROID_IMAGE_SIZE = 72
MISSILE_IMAGE_SIZE = 16
ANGLE_STEP = 5

# Параметры космического фона.
BACKGROUND_SPEED = 28
BACKGROUND_ROCK_COUNT = 30
BACKGROUND_ROCK_SIZE = 30
BACKGROUND_ALPHA = 65
STAR_COUNT = 240

# Размеры стартовой заставки.
SPLASH_WIDTH = 440
SPLASH_HEIGHT = 220

# Цвета элементов игры.
BACKGROUND_COLOR = "#070a1e"
WHITE = "#f0f5ff"
GREEN = "#64ff96"
BLUE = "#5591ff"
SPLASH_COLOR = "#0f1941"
