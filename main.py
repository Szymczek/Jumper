import random
import pygame
from config import *
from sprites import *
from os import path


class Game:
    def __init__(self):
        # initialize game window, etc
        self.running = True
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font_name = pygame.font.match_font(FONT_NAME)
        self.load_data()
        self.mob_timer = 0
    def load_data(self):
        # load highscore
        self.dir = path.dirname(__file__)
        self.img_dir = path.join(self.dir, 'img')
        try:
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                self.highscore = int(f.read())
        except:
            with open(path.join(self.dir, HS_FILE), 'w'):
                self.highscore = 0
        # load spritesheet
        self.spritesheet = Spritesheet(path.join(self.img_dir, SPRITESHEET))
        # load clouds
        self.cloud_images = []
        for i in range(1, 4):
            self.cloud_images.append(pygame.image.load(path.join(self.img_dir, 'cloud{}.png'.format(i))).convert())
        # load sound
        self.snd_dir = path.join(self.dir, 'snd')
        self.jump_sound = pygame.mixer.Sound(path.join(self.snd_dir, 'jump_snd.wav'))
        self.boost_sound = pygame.mixer.Sound(path.join(self.snd_dir, 'boost.wav'))
        self.jump_sound.set_volume(0.05)
        self.boost_sound.set_volume(0.3)

    def new(self):
        # start a new game
        self.score = 0
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.platforms = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.clouds = pygame.sprite.Group()
        self.player = Player(self)
        for platform in PLATFORM_LIST:
            Platform(self, *platform)
        pygame.mixer.music.load(path.join(self.snd_dir, 'Winds Of Stories.ogg'))
        for i in range(10):
            c = Cloud(self)
            c.rect.y += 500
        self.run()

    def run(self):
        # Game loop
        pygame.mixer.music.play(loops=-1)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pygame.mixer.music.fadeout(500)

    def update(self):
        # Game Loop - Update
        self.all_sprites.update()
        if self.player.vel.y > 0:
            hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if self.player.pos.x < lowest.rect.right + 10 and \
                   self.player.pos.x > lowest.rect.left - 10:
                    if self.player.pos.y < lowest.rect.centery:
                        self.player.pos.y = lowest.rect.top
                        self.player.vel.y = 0
                        self.player.jumping = False
        # spawn a mob
        now = pygame.time.get_ticks()
        if now - self.mob_timer > 5000 + random.choice([-1000, 4, -4, 599, 499]):
            self.mob_timer = now
            Mob(self)
        # if player reaches top 1/4 of screen
        if self.player.rect.top <= HEIGHT / 2:
            if random.randrange(100) < 15 :
                Cloud(self)
            self.player.pos.y += max(abs(self.player.vel.y), 2)
            for cloud in self.clouds:
                cloud.rect.y += max(abs(self.player.vel.y / 2), 2)
            for mob in self.mobs:
                mob.rect.y += max(abs(self.player.vel.y), 2)
            for platform in self.platforms:
                platform.rect.y += max(abs(self.player.vel.y), 2)
                if platform.rect.top >= HEIGHT:
                    platform.kill()
                    self.score += 1

        # spawn new platform
        while len(self.platforms) < 7:
            width = random.randrange(50, 100)
            Platform(self, random.randrange(0, WIDTH-width), random.randrange(-75, -30))
        # if player hits mob
        mob_hits = pygame.sprite.spritecollide(self.player, self.mobs, False, pygame.sprite.collide_mask)
        if mob_hits:
            self.playing = False
        # if player hits powerup
        pow_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for pow in pow_hits:
            if pow.type == 'boost':
                self.boost_sound.play()
                self.player.vel.y =- BOOST_POWER
                self.player.jumping = False
        # Die
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.playing = False
            # self.playing = False
            # self.player.kill()

    def events(self):
        # Game Loop - events
        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.jump()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.player.jump_cut()

    def draw(self):
        # Game Loop - draw
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), 18, WHITE, 10, 20)
        pygame.display.flip()

    def show_start_screen(self):
        pygame.mixer.music.load(path.join(self.snd_dir, 'TownTheme.ogg'))
        pygame.mixer.music.play(loops=-1)
        pygame.mixer.music.set_volume(0.05)
        self.screen.fill(BGCOLOR)
        self.draw_text("JUMPY", 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("WSAD to move, space to jump", 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press a key to play", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        self.draw_text("High Score: " + str(self.highscore), 22, WHITE, WIDTH / 2, 15)
        pygame.display.flip()
        self.wait_for_key()
        pygame.mixer.music.fadeout(500)

    def show_go_screen(self):
        pygame.mixer.music.load(path.join(self.snd_dir, 'TownTheme.ogg'))
        pygame.mixer.music.play(loops=-1)
        pygame.mixer.music.set_volume(0.05)
        if not self.running:
            return
        self.screen.fill(BGCOLOR)
        self.draw_text("GAME OVER", 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Score: " + str(self.score), 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press a key to play again", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("NEW HIGH SCORE!", 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.score))
        else:
            self.draw_text("High Score: " + str(self.highscore), 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
        pygame.display.flip()
        self.wait_for_key()
        pygame.mixer.music.fadeout(500)

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYUP:
                    waiting = False

    def draw_text(self, text, size, color, x, y):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)


game = Game()
game.show_start_screen()
while game.running:
    game.new()
    game.show_go_screen()
pygame.quit()
