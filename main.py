import sys
from sprites import *
from map_render import *
from settings import *
from os import path, listdir
import random
import ctypes

# music event for switching music
MUSIC_ENDED = pg.USEREVENT
pg.mixer.music.set_endevent(MUSIC_ENDED)

# windows taskbar icon
myappid = 'mycompany.myproduct.subproduct.version'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


# load images from folder function
def load_images_from_folder(folder):
    images = []
    for filename in listdir(folder):
        if '.png' in path.join(folder, filename):
            img = pg.image.load(path.join(folder, filename))
            images.append(pg.transform.scale(img, (TILESIZE, TILESIZE)))
    return images


# sounds loading function
def load_sounds_from_folder(folder):
    sounds = []
    for filename in listdir(folder):
        if '.mp3' in path.join(folder, filename):
            sounds.append(path.join(folder, filename))
    return sounds


# game class
class Game:
    def __init__(self):
        pg.init()
        # getting display info
        self.infoObject = pg.display.Info()
        self.screen_info = (self.infoObject.current_w, self.infoObject.current_h)
        # screen init
        self.screen = pg.display.set_mode(self.screen_info, pg.FULLSCREEN)
        # setting caption
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        # loading data
        self.load_data()

    def load_data(self):
        # loading folders
        self.game_folder = path.dirname(__file__)
        map_folder = path.join(self.game_folder, 'map')
        self.sprites_folder = path.join(self.game_folder, 'sprites')
        self.snail_folder = path.join(self.sprites_folder, 'snail_images')
        self.features_folder = path.join(self.game_folder, 'features')
        self.sounds_folder = path.join(self.features_folder, 'sounds')
        self.font_folder = path.join(self.features_folder, 'fonts')

        # loading icon
        icon = pg.transform.scale(pg.image.load(path.join(self.snail_folder, ICON_IMAGE)), (TILESIZE, TILESIZE))
        pg.display.set_icon(icon)

        # loading font
        self.font = path.join(self.font_folder, 'pixel_font.ttf')

        # loading map
        self.map = TiledMap(path.join(map_folder, 'map.tmx'))
        self.map_image = self.map.make_map()
        self.map_rect = self.map_image.get_rect()

        # loading player animations
        self.load_player_sprites()

        # loading item images
        self.item_images = {}
        self.food_folder = path.join(self.sprites_folder, 'food')
        for item in ITEM_IMAGES:
            self.item_images[item] = pg.transform.scale(
                pg.image.load(path.join(self.food_folder, ITEM_IMAGES[item])).convert_alpha(), (20, 20))
        self.item_rect = self.item_images['apple'].get_rect()

        # setting available items
        self.food_counter = 0

        # loading sounds
        self.songs = load_sounds_from_folder(self.sounds_folder)
        self.song_index = 0

    def load_player_sprites(self):
        # loading animations
        self.standing_animation = load_images_from_folder(path.join(self.snail_folder, 'standing'))
        self.moving_forward = load_images_from_folder(path.join(self.snail_folder, 'moving_forward'))
        self.moving_down = load_images_from_folder(path.join(self.snail_folder, 'moving_down'))
        self.moving_right = load_images_from_folder(path.join(self.snail_folder, 'moving_right'))
        self.moving_left = load_images_from_folder(path.join(self.snail_folder, 'moving_left'))
        self.moving_down_right = load_images_from_folder(path.join(self.snail_folder, 'moving_down_right'))
        self.moving_down_left = load_images_from_folder(path.join(self.snail_folder, 'moving_down_left'))
        self.moving_left_up = load_images_from_folder(path.join(self.snail_folder, 'moving_forward_left'))
        self.moving_right_up = load_images_from_folder(path.join(self.snail_folder, 'moving_forward_right'))
        self.housing_animation = load_images_from_folder(path.join(self.snail_folder, 'housing_animation'))
        self.house = load_images_from_folder(path.join(self.snail_folder, 'house'))

    def new(self):
        # setting sprite groups
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.items = pg.sprite.Group()
        # setting score
        self.score = 0
        # loading map hitboxes and spawning the player
        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == 'player':
                self.player = Player(self, tile_object.x, tile_object.y)
            if tile_object.name == 'obstacle':
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
        # loading camera
        self.camera = Camera(self.map.width, self.map.height)

    def run(self):


        # making main game loop
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    # quit functions
    def quit(self):
        pg.quit()
        sys.exit()

    # updating game information
    def update(self):
        # updating sprites
        self.all_sprites.update()
        # updating camera
        self.camera.update(self.player)
        # collecting food check
        hits = pg.sprite.spritecollide(self.player, self.items, True)
        for hit in hits:
            if hit.type == 'apple' or hit.type == 'cherry':
                hit.kill()
                self.player.add_speed(random.randrange(3, 20))
                self.score += 1
        # spawning food loop
        if self.food_counter < 35:
            self.random_food_spawn()

    # food spawning function
    def random_food_spawn(self):
        coords = random.choice(self.ok_coords)
        Item(self, coords, random.choice(['cherry', 'apple']))
        self.food_counter += 1

    # loading available positions for food spawning
    def load_positions(self):
        self.ok_coords = []
        # loading positions from file
        with open(path.join(self.game_folder, 'positions.txt'), 'r') as f:
            for line in f:
                new = eval(line[:-1])
                self.ok_coords.append(new)

    # displaying the game on the screen
    def draw(self):
        # displaying map
        self.screen.blit(self.map_image, self.camera.apply_rect(self.map_rect))
        # displaying sprites
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        # displaying text
        self.draw_text(f'Speed: {self.player.speed}', self.font, 25, WHITE, self.screen_info[0] - 10,
                       10, align='ne')
        self.draw_text(f'Score: {self.score}', self.font, 25, WHITE, self.screen_info[0] - 10,
                       45, align='ne')
        pg.display.update()

    def events(self):
        # getting events from user
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
            try:
                if event.type == MUSIC_ENDED:
                    if self.song_index + 1 == len(self.songs):
                        self.song_index = 0
                    else:
                        self.song_index = self.song_index + 1
                    pg.mixer.music.load(self.songs[self.song_index])
                    pg.mixer.music.set_volume(0.3)
                    pg.mixer.music.play()
            except Exception:
                pass

    # text drawing function
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

    # start screen function
    def show_start_screen(self):
        # playing first song
        try:
            pg.mixer.music.load(self.songs[self.song_index])
            pg.mixer.music.set_volume(0.3)
            pg.mixer.music.play()
        except Exception:
            pass
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
        self.draw_text("Eat food and speed up. Discover new fantastic places!", self.font, 22, BLACK,
                       self.screen_info[0] / 2,
                       self.screen_info[1] * 3 / 5, align='center')
        self.draw_text("Press a key to play", self.font, 22, BLACK, self.screen_info[0] / 2,
                       self.screen_info[1] * 5 / 7, align='center')
        pg.display.flip()
        self.wait_for_key()
        self.load_positions()

    # waiting for key to load the game
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


# starting the program
g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
