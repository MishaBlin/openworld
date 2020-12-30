import sys
from sprites import *
from map_render import *
from os import *
import random


def load_images_from_folder(folder):
    images = []
    for filename in listdir(folder):
        img = pg.image.load(path.join(folder, filename))
        images.append(pg.transform.scale(img, (32, 32)))
    return images


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT), pg.FULLSCREEN)
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        self.load_data()

    def load_data(self):
        game_folder = path.dirname(__file__)
        map_folder = path.join(game_folder, 'map')
        self.sprites_folder = path.join(game_folder, 'sprites')

        self.map = TiledMap(path.join(map_folder, 'map.tmx'))
        self.map_image = self.map.make_map()
        self.map_rect = self.map_image.get_rect()

        self.load_player_sprites()

        self.item_images = {}
        for item in ITEM_IMAGES:
            self.item_images[item] = pg.transform.scale(
                pg.image.load(path.join(self.sprites_folder, ITEM_IMAGES[item])).convert_alpha(), (20, 20))

    def load_player_sprites(self):
        snail_folder = path.join(self.sprites_folder, 'snail_images')
        self.standing_animation = load_images_from_folder(path.join(snail_folder, 'standing'))
        self.moving_forward = load_images_from_folder(path.join(snail_folder, 'moving_forward'))
        self.moving_down = load_images_from_folder(path.join(snail_folder, 'moving_down'))
        self.moving_right = load_images_from_folder(path.join(snail_folder, 'moving_right'))
        self.moving_left = load_images_from_folder(path.join(snail_folder, 'moving_left'))
        self.moving_down_right = load_images_from_folder(path.join(snail_folder, 'moving_down_right'))
        self.moving_down_left = load_images_from_folder(path.join(snail_folder, 'moving_down_left'))
        self.moving_left_up = load_images_from_folder(path.join(snail_folder, 'moving_forward_left'))
        self.moving_right_up = load_images_from_folder(path.join(snail_folder, 'moving_forward_right'))
        self.death_animation = load_images_from_folder(path.join(snail_folder, 'death'))
        self.housing_animation = load_images_from_folder(path.join(snail_folder, 'housing_animation'))
        self.reversed_housing = self.housing_animation[::-1]
        self.house = load_images_from_folder(path.join(snail_folder, 'house'))

    def new(self):
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.items = pg.sprite.Group()
        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == 'player':
                self.player = Player(self, tile_object.x, tile_object.y)
            if tile_object.name == 'obstacle':
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
        Item(self, (random.randrange(1, self.map.width), random.randrange(1, self.map.height)), 'apple')
        self.camera = Camera(self.map.width, self.map.height)

    def run(self):
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)
        hits = pg.sprite.spritecollide(self.player, self.items, True)
        for hit in hits:
            if hit.type == 'apple':
                hit.kill()
                self.player.add_speed(SPEED_BY_APPLE)
                # Item(self, (random.randrange(1, self.map.width), random.randrange(1, self.map.height)), 'apple')
                Item(self, (random.randrange(1, self.map.width), random.randrange(1, self.map.height)), 'apple')

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        # self.screen.fill(BGCOLOR)
        # self.draw_grid()
        self.screen.blit(self.map_image, self.camera.apply_rect(self.map_rect))
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        pg.display.flip()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        pass


g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_go_screen()
