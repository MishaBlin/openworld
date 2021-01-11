import sys
from sprites import *
from map_render import *
from os import *
import random
import ctypes

myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


def load_images_from_folder(folder):
    images = []
    for filename in listdir(folder):
        if '.png' in path.join(folder, filename):
            img = pg.image.load(path.join(folder, filename))
            images.append(pg.transform.scale(img, (32, 32)))
    return images


class Game:
    def __init__(self):
        pg.init()
        self.infoObject = pg.display.Info()
        self.screen_info = (self.infoObject.current_w, self.infoObject.current_h)
        self.screen = pg.display.set_mode(self.screen_info)
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        self.load_data()

    def load_data(self):
        game_folder = path.dirname(__file__)
        map_folder = path.join(game_folder, 'map')
        self.sprites_folder = path.join(game_folder, 'sprites')
        self.snail_folder = path.join(self.sprites_folder, 'snail_images')
        self.features_folder = path.join(game_folder, 'features')
        self.sounds_folder = path.join(self.features_folder, 'sounds')
        self.font_folder = path.join(self.features_folder, 'fonts')

        icon = pg.transform.scale(pg.image.load(path.join(self.snail_folder, ICON_IMAGE)), (32, 32))
        pg.display.set_icon(icon)

        self.font = path.join(self.font_folder, 'pixel_font.ttf')

        self.map = TiledMap(path.join(map_folder, 'map.tmx'))
        self.map_image = self.map.make_map()
        self.map_rect = self.map_image.get_rect()

        self.load_player_sprites()

        self.item_images = {}
        self.food_folder = path.join(self.sprites_folder, 'food')
        for item in ITEM_IMAGES:
            self.item_images[item] = pg.transform.scale(
                pg.image.load(path.join(self.food_folder, ITEM_IMAGES[item])).convert_alpha(), (20, 20))
        try:
            pg.mixer.music.load(path.join(self.sounds_folder, BG_MUSIC))
        except Exception:
            pass

    def load_player_sprites(self):
        self.standing_animation = load_images_from_folder(path.join(self.snail_folder, 'standing'))
        self.moving_forward = load_images_from_folder(path.join(self.snail_folder, 'moving_forward'))
        self.moving_down = load_images_from_folder(path.join(self.snail_folder, 'moving_down'))
        self.moving_right = load_images_from_folder(path.join(self.snail_folder, 'moving_right'))
        self.moving_left = load_images_from_folder(path.join(self.snail_folder, 'moving_left'))
        self.moving_down_right = load_images_from_folder(path.join(self.snail_folder, 'moving_down_right'))
        self.moving_down_left = load_images_from_folder(path.join(self.snail_folder, 'moving_down_left'))
        self.moving_left_up = load_images_from_folder(path.join(self.snail_folder, 'moving_forward_left'))
        self.moving_right_up = load_images_from_folder(path.join(self.snail_folder, 'moving_forward_right'))
        self.death_animation = load_images_from_folder(path.join(self.snail_folder, 'death'))
        self.housing_animation = load_images_from_folder(path.join(self.snail_folder, 'housing_animation'))
        self.house = load_images_from_folder(path.join(self.snail_folder, 'house'))

    def new(self):
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.rituals = pg.sprite.Group()
        self.forbidden_coords = []
        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == 'player':
                self.player = Player(self, tile_object.x, tile_object.y)
            if tile_object.name == 'obstacle':
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
                self.forbidden_coords.append((int(tile_object.x), int(tile_object.y)))
                for width in range(int(tile_object.width)):
                    for height in range(int(tile_object.height)):
                        self.forbidden_coords.append((int(tile_object.x) + width, int(tile_object.y) + height))
        self.random_apple_spawn((93 * 32, 158 * 32), (61 * 32, 99 * 32))
        # TODO

        for _ in range(25):
            self.random_apple_spawn((32, self.map.width), (32, self.map.height))
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
            if hit.type == 'apple' or hit.type == 'cherry':
                hit.kill()
                if self.player.speed < 500:
                    self.player.add_speed(SPEED_BY_ITEM)
                if self.player.speed >= 400:
                    self.random_apple_spawn((32, self.map.width), (32, self.map.height))
                else:
                    self.random_apple_spawn((93 * 32, 158 * 32), (61 * 32, 99 * 32))

    def random_apple_spawn(self, range_x, range_y):
        item_x = random.randrange(range_x[0], range_x[1])
        item_y = random.randrange(range_y[0], range_y[1])
        while (item_x, item_y) in self.forbidden_coords:
            item_x = random.randrange(range_x[0], range_x[1])
            item_y = random.randrange(range_y[0], range_y[1])
        Item(self, (item_x, item_y), random.choice(['cherry', 'apple']))

    def draw(self):
        self.screen.blit(self.map_image, self.camera.apply_rect(self.map_rect))
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        self.draw_text(f'Speed: {self.player.speed}', self.font, 25, WHITE, self.screen_info[0] - 10,
                       10, align='ne')
        pg.display.update()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()

    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        if align == "ne":
            text_rect.topright = (x, y)
        if align == "sw":
            text_rect.bottomleft = (x, y)
        if align == "se":
            text_rect.bottomright = (x, y)
        if align == "n":
            text_rect.midtop = (x, y)
        if align == "s":
            text_rect.midbottom = (x, y)
        if align == "e":
            text_rect.midright = (x, y)
        if align == "w":
            text_rect.midleft = (x, y)
        if align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def show_start_screen(self):
        bg_image = pg.transform.scale(pg.image.load(path.join(self.sprites_folder, BG_IMAGE)), self.screen_info)
        self.screen.blit(bg_image, (0, 0))
        self.draw_text(f'Welcome to', self.font, 22, BLACK, self.screen_info[0] / 2, self.screen_info[1] / 5,
                       align='center')
        self.draw_text(TITLE.upper(), self.font, 48, BLACK,
                       self.screen_info[0] / 2,
                       self.screen_info[1] / 3, align='center')
        self.draw_text("Use w,a,s,d to move, space to hide and escape to exit", self.font, 22, BLACK,
                       self.screen_info[0] / 2,
                       self.screen_info[1] / 2, align='center')
        self.draw_text("Press a key to play", self.font, 22, BLACK, self.screen_info[0] / 2,
                       self.screen_info[1] * 3 / 5, align='center')
        pg.display.flip()
        try:
            pg.mixer.music.play(loops=-1)
        except Exception:
            pass
        self.wait_for_key()

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False


g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
