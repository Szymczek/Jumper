
TITLE = "Jumper"
WIDTH = 480
HEIGHT = 600
FPS = 60
FONT_NAME = 'Arial'
HS_FILE = "highscore.txt"
SPRITESHEET = "jumper.png"
# Player properties
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.05
PLAYER_GRAV = 0.5
PLAYER_JUMP = 25
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BGCOLOR = (0, 0, 150)
# Starting platforms
PLATFORM_LIST = [(0, HEIGHT - 60),
                 (WIDTH / 2 - 100, HEIGHT - 200),
                 (125, HEIGHT - 350),
                 (175, 200),
                 (350, 100)]
# Game properties
BOOST_POWER = 60
POW_SPAWN_PCT = 7
MOB_FREQ = 5000
PLAYER_LAYER = 2
PLATFORM_LAYER = 1
POW_LAYER = 1
MOB_LAYER = 2
CLOUD_LAYER = 0

