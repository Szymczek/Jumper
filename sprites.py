# Sprites
import random

import pygame
from config import *
from random import choice, randrange
vec = pygame.math.Vector2


class Spritesheet:
    # class for loading and parsing spritesheets

    def __init__(self, filename):
        self.spreatsheet = pygame.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # grab on image out of a larger spritesheet
        image = pygame.Surface((width, height))
        image.blit(self.spreatsheet, (0, 0), (x, y, width, height))
        image = pygame.transform.scale(image, (width // 2, height // 2))
        return image


class Player(pygame.sprite.Sprite):

    def __init__(self, game):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.walking = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.standing_frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (40, HEIGHT - 100 )
        self.pos = vec(40, HEIGHT - 100)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def load_images(self):
        self.standing_frames = [self.game.spritesheet.get_image(614, 1063, 120, 191),
                                self.game.spritesheet.get_image(690, 406, 120, 201)]
        self.walk_frames_r = [self.game.spritesheet.get_image(678, 860, 120, 201),
                              self.game.spritesheet.get_image(692, 1458, 120, 207)]
        for frame in self.standing_frames:
            frame.set_colorkey(BLACK)
        self.walk_frames_l = []
        for frame in self.walk_frames_r:
            frame.set_colorkey(BLACK)
            self.walk_frames_l.append(pygame.transform.flip(frame, True, False))
        self.jump_frame = self.game.spritesheet.get_image(382, 763, 150, 181)
        self.jump_frame.set_colorkey(BLACK)

    def jump(self):
        # jump on a platform
        self.rect.y += 2
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.y -= 2
        if hits and not self.jumping:
            self.game.jump_sound.play()
            self.jumping = True
            self.vel.y -= PLAYER_JUMP

    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -3:
                self.vel.y = -3

    def update(self):
        self.animate()
        self.acc = vec(0, PLAYER_GRAV)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.acc.x = PLAYER_ACC
        if keys[pygame.K_a]:
            self.acc.x = -PLAYER_ACC
        # Apply friction
        self.acc.x += self.vel.x * PLAYER_FRICTION
        # Equations of motion
        self.vel += self.acc
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc
        # wrap around the sides of the screen
        if self.pos.x > WIDTH + self.rect.width / 2:
            self.pos.x = 0 - self.rect.width / 2
        if self.pos.x < 0 - self.rect.width / 2:
            self.pos.x = WIDTH + self.rect.width / 2
        self.rect.midbottom = self.pos

    def animate(self):
        now = pygame.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False
        # show walk animation\
        if self.walking:
            if now - self.last_update > 220:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                if self.vel.x > 0:
                    self.image = self.walk_frames_r[self.current_frame]
                else:
                    self.image = self.walk_frames_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        # show idle animation
        if not self.jumping and not self.walking:
            if now - self.last_update > 600:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        self.mask = pygame.mask.from_surface(self.image)

class Platform(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLATFORM_LAYER
        self.groups = game.all_sprites, game.platforms
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        images = [self.game.spritesheet.get_image(0, 288, 380, 94),
                  self.game.spritesheet.get_image(213, 1662, 201, 100)]
        self.image = choice(images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        if randrange(100) < POW_SPAWN_PCT:
            Pow(self.game, self)

    def update(self):
        pass


class Pow(pygame.sprite.Sprite):
    def __init__(self, game, plat):
        self._layer = POW_LAYER
        self.groups = game.all_sprites, game.powerups
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.type = choice(['boost'])
        self.image = self.game.spritesheet.get_image(820, 1805, 71, 70)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5

    def update(self):
        self.rect.bottom = self.plat.rect.top - 5
        if not self.game.platforms.has(self.plat):
            self.kill()


class Mob(pygame.sprite.Sprite):
    def __init__(self, game):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.loading_data()
        self.image = self.flying_frames[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = choice([0, WIDTH + 100])
        self.vx = randrange(1, 4)
        if self.rect.centerx > WIDTH:
            self.vx *= -1
        self.rect.y = randrange(HEIGHT / 2)
        self.vy = 0
        self.dy = 0.5

    def update(self):
        self.rect.x += self.vx
        self.vy += self.dy
        if self.vy > 3 or self.vy < - 3:
            self.dy *= -1
        center = self.rect.center
        if self.dy < 0:
            self.image = self.flying_frames[1]
        else:
            self.image = self.flying_frames[2]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.rect.y += self.vy
        self.mask = pygame.mask.from_surface(self.image)
        if self.rect.left > WIDTH + 100 or self.rect.right < - 100:
            self.kill()


    def loading_data(self):
        self.flying_frames = [self.game.spritesheet.get_image(382, 635, 174, 126),
                                self.game.spritesheet.get_image(0, 1879, 206, 107),
                                self.game.spritesheet.get_image(0, 1559, 216, 101),
                                self.game.spritesheet.get_image(0, 1456, 216, 101),
                                self.game.spritesheet.get_image(382, 510, 182, 123)]
        for frame in self.flying_frames:
            frame.set_colorkey(BLACK)

class Cloud(pygame.sprite.Sprite):
    def __init__(self, game):
        self._layer = CLOUD_LAYER
        self.groups = game.all_sprites, game.clouds
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = choice(self.game.cloud_images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        scale = randrange(50,101) / 100
        self.image = pygame.transform.scale(self.image, (int(self.rect.width * scale), int(self.rect.height * scale)))
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-500, 0)

    def update(self):
       if self.rect.top > HEIGHT * 2:
            self.kill()
