import pygame as pg
from settings import *
import pytweening as tween

vec = pg.math.Vector2


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.animation = 'standing'
        self.animation_standing = game.standing_animation
        self.animation_right = game.moving_right
        self.animation_left = game.moving_left
        self.animation_forward = game.moving_forward
        self.animation_forward_right = game.moving_right_up
        self.animation_forward_left = game.moving_left_up
        self.animation_down_left = game.moving_down_left
        self.animation_down = game.moving_down
        self.animation_death = game.death_animation
        self.animation_down_right = game.moving_down_right
        self.house_animation = game.house
        self.housing_animation = game.housing_animation
        self.reversed_housing = game.reversed_housing
        self.current_sprite = 0
        self.image = self.animation_right[self.current_sprite]
        self.animate = True
        self.in_house = False
        self.w = True
        self.d = True
        self.a = True
        self.s = True

        self.rect = self.image.get_rect()
        self.vel = vec(0, 0)
        self.y = y
        self.pos = vec(x, y)
        self.speed = PLAYER_SPEED

    def get_keys(self):
        if not self.in_house:
            self.w = True
            self.d = True
            self.a = True
            self.s = True
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        if not self.in_house:
            if keys[pg.K_w] and keys[pg.K_d]:
                self.w = False
                self.d = False
                self.vel.x = self.speed
                self.vel.y = -self.speed
                self.animate = True
                self.animation = 'forward_right'
        if not self.in_house:
            if keys[pg.K_a] and keys[pg.K_w]:
                self.w = False
                self.a = False
                self.vel.x = -self.speed
                self.vel.y = -self.speed
                self.animate = True
                self.animation = 'forward_left'
        if not self.in_house:
            if keys[pg.K_a] and keys[pg.K_s]:
                self.s = False
                self.a = False
                self.vel.x = -self.speed
                self.vel.y = self.speed
                self.animate = True
                self.animation = 'down_left'

        if not self.in_house:
            if keys[pg.K_d] and keys[pg.K_s]:
                self.s = False
                self.d = False
                self.vel.y = self.speed
                self.vel.x = self.speed
                self.animate = True
                self.animation = 'down_right'

        if self.a:
            if keys[pg.K_LEFT] or keys[pg.K_a]:
                self.vel.x = -self.speed
                self.animate = True
                self.animation = 'left'

        if self.d:
            if keys[pg.K_RIGHT] or keys[pg.K_d]:
                self.vel.x = self.speed
                self.animate = True
                self.animation = 'right'
        if self.s:
            if keys[pg.K_DOWN] or keys[pg.K_s]:
                self.vel.y = self.speed
                self.animate = True
                self.animation = 'down'
        if self.w:
            if keys[pg.K_UP] or keys[pg.K_w]:
                self.vel.y = -self.speed
                self.animate = True
                self.animation = 'forward'

        if keys[pg.K_SPACE]:
            pg.time.wait(100)
            self.in_house = not self.in_house
            if self.in_house:
                self.w = False
                self.s = False
                self.a = False
                self.d = False
                self.vel.y = 0
                self.vel.x = 0
                self.animate = True
                self.animation = 'housing'

        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071

    def occupied_with_object(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.x > 0:
                    self.pos.x = hits[0].rect.left - self.rect.width
                if self.vel.x < 0:
                    self.pos.x = hits[0].rect.right
                self.vel.x = 0
                self.rect.x = self.pos.x
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.rect.height
                if self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom
                self.vel.y = 0
                self.rect.y = self.pos.y

    def add_speed(self, amount):
        self.speed += amount

    def update(self):
        self.get_keys()
        self.pos += self.vel * self.game.dt
        self.rect.x = self.pos.x
        self.occupied_with_object('x')
        self.rect.y = self.pos.y
        self.occupied_with_object('y')
        if self.vel.y == 0 and self.vel.x == 0 and not self.in_house:
            self.animation = 'standing'
            self.animate = True

        if self.animate:
            if self.animation == 'right':
                self.__create_animation__(0.05, self.animation_right)

            if self.animation == 'left':
                self.__create_animation__(0.05, self.animation_left)

            if self.animation == 'forward':
                self.__create_animation__(0.05, self.animation_forward)

            if self.animation == 'forward_right':
                self.__create_animation__(0.05, self.animation_forward_right)

            if self.animation == 'forward_left':
                self.__create_animation__(0.05, self.animation_forward_left)

            if self.animation == 'standing':
                self.__create_animation__(0.03, self.animation_standing)

            if self.animation == 'down_left':
                self.__create_animation__(0.05, self.animation_down_left)

            if self.animation == 'down_right':
                self.__create_animation__(0.05, self.animation_down_right)

            if self.animation == 'down':
                self.__create_animation__(0.05, self.animation_down)

            if self.animation == 'death':
                self.__create_animation__(0.05, self.animation_death)

            if self.animation == 'housing':
                self.current_sprite += 0.15

                if self.current_sprite >= len(self.housing_animation):
                    self.current_sprite = len(self.housing_animation) - 1

                self.image = self.housing_animation[int(self.current_sprite)]

    def __create_animation__(self, speed, name):
        self.current_sprite += speed

        if self.current_sprite >= len(name):
            self.current_sprite = 0
            self.animate = False

        self.image = name[int(self.current_sprite)]


class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


class Item(pg.sprite.Sprite):
    def __init__(self, game, pos, type):
        self._layer = ITEMS_LAYER
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.item_images[type]
        self.rect = self.image.get_rect()
        self.type = type
        self.rect.center = pos
        self.pos = pos
        self.tween = tween.easeInOutQuart
        self.step = 0
        self.direction = 1

    def update(self):
        offset = BOB_RANGE * (self.tween(self.step / BOB_RANGE) - 0.5)
        self.rect.centery = self.pos[1] + offset * self.direction
        self.step += BOB_SPEED
        if self.step > BOB_RANGE:
            self.step = 0
            self.direction *= -1
