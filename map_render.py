import pygame as pg
import pytmx


# rendering tiled map using pytmx
class TiledMap:
    def __init__(self, filename):
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm
        self.players = pytmx.TiledImageLayer
        self.objects = pytmx.TiledImageLayer

    def render(self, surface, sender):
        if sender == 'map':
            ti = self.tmxdata.get_tile_image_by_gid
            for layer in self.tmxdata.visible_layers:
                if isinstance(layer, pytmx.TiledTileLayer):
                    for x, y, gid, in layer:
                        tile = ti(gid)
                        if tile:
                            surface.blit(tile, (x * self.tmxdata.tilewidth, y * self.tmxdata.tileheight))

    def make_map(self):
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface, 'map')
        return temp_surface


# making camera
class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        infoObject = pg.display.Info()
        self.sizes = (infoObject.current_w, infoObject.current_h)

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    # updating camera
    def update(self, target):
        x = -target.rect.x + int(self.sizes[0] / 2)
        y = -target.rect.y + int(self.sizes[1] / 2)

        x = min(0, x)
        y = min(0, y)
        x = max(-(self.width - self.sizes[0]), x)
        y = max(-(self.height - self.sizes[1]), y)
        self.camera = pg.Rect(x, y, self.width, self.height)
