import os
import pygame
import collections
import Service

colors = {
    "black": (0, 0, 0, 255),
    "white": (255, 255, 255, 255),
    "red": (255, 0, 0, 255),
    "green": (0, 255, 0, 255),
    "blue": (0, 0, 255, 255),
    "wooden": (153, 92, 0, 255),
}


class ScreenHandle(pygame.Surface):

    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            self.successor = args[-1]
            self.next_coord = args[-2]
            args = args[:-2]
        else:
            self.successor = None
            self.next_coord = (0, 0)
        super().__init__(*args, **kwargs)
        self.fill(colors["wooden"])

    def draw(self, canvas):
        if self.successor is not None:
            canvas.blit(self.successor, self.next_coord)
            self.successor.draw(canvas)

    def connect_engine(self, engine):
        if self.successor is not None:
            self.successor.connect_engine(engine)


class GameSurface(ScreenHandle):

    def connect_engine(self, engine):
        self.game_engine = engine
        super().connect_engine(engine)

    def calculate(self):
        hero_x = self.game_engine.hero.position[0]
        hero_y = self.game_engine.hero.position[1]

        half_screen_x = self.game_engine.screen_size[0] / 2
        half_screen_y = self.game_engine.screen_size[1] / 2

        map_size_x = len(self.game_engine.map[0])
        map_size_y = len(self.game_engine.map[1])

        if hero_x < half_screen_x:
            min_x = 0
        elif hero_x > map_size_x - half_screen_x:
            min_x = map_size_x - half_screen_x*2
        else:
            min_x = hero_x - half_screen_x

        if hero_y < half_screen_y:
            min_y = 0
        elif hero_y > map_size_y - half_screen_y:
            min_y = map_size_y - half_screen_y*2
        else:
            min_y = hero_y - half_screen_y

        self.game_engine.padding = int(min_x), int(min_y)

        return int(min_x), int(min_y)

    def draw_hero(self):
        self.game_engine.hero.draw(self)

    def draw_map(self):
        size = self.game_engine.sprite_size
        min_x, min_y = self.calculate()

        if self.game_engine.map:
            for i in range(len(self.game_engine.map[0]) - min_x):
                for j in range(len(self.game_engine.map) - min_y):
                    self.blit(self.game_engine.map[min_y + j][min_x + i][
                              0], (i * size, j * size))
        else:
            self.fill(colors["white"])

    def draw_object(self, sprite, coord):
        size = self.game_engine.sprite_size
        min_x, min_y = self.calculate()

        self.blit(sprite, ((coord[0] - min_x) * size,
                           (coord[1] - min_y) * size))

    def draw(self, canvas):
        size = self.game_engine.sprite_size
        min_x, min_y = self.calculate()

        self.draw_map()
        for obj in self.game_engine.objects:
            self.blit(obj.sprite[0], ((obj.position[0] - min_x) * size,
                                      (obj.position[1] - min_y) * size))
        self.draw_hero()
        # draw next surface in chain
        super().draw(canvas)


class MiniMap(ScreenHandle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def connect_engine(self, engine):
        self.game_engine = engine
        super().connect_engine(engine)

    def draw(self, canvas):
        size = 4

        if self.game_engine.map:
            for i in range(len(self.game_engine.map[0])):
                for j in range(len(self.game_engine.map)):
                    self.blit(self.game_engine.map[j][i][
                              0], (i * size, j * size))
            mini_hero = Service.create_sprite(os.path.join("texture", "Hero.png"), size)

            self.blit(mini_hero, (self.game_engine.hero.position[0] * size, self.game_engine.hero.position[1] * size))
        else:
            self.fill(colors["white"])
        super().draw(canvas)


class ProgressBar(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fill(colors["wooden"])

    def connect_engine(self, engine):
        self.engine = engine
        super().connect_engine(engine)

    def draw(self, canvas):
        self.fill(colors["wooden"])
        pygame.draw.rect(self, colors["black"], (50, 30, 200, 30), 2)
        pygame.draw.rect(self, colors["black"], (50, 70, 200, 30), 2)

        pygame.draw.rect(self, colors[
                         "red"], (50, 30, 200 * self.engine.hero.hp / self.engine.hero.max_hp, 30))
        pygame.draw.rect(self, colors["green"], (50, 70,
                                                 200 * self.engine.hero.exp / (100 * (2**(self.engine.hero.level - 1))), 30))

        font = pygame.font.SysFont("comicsansms", 20)
        self.blit(font.render(f'Hero at {self.engine.hero.position}', True, colors["black"]),
                  (250, 0))

        self.blit(font.render(f'{self.engine.level} floor', True, colors["black"]),
                  (10, 0))

        self.blit(font.render(f'HP', True, colors["black"]),
                  (10, 30))
        self.blit(font.render(f'Exp', True, colors["black"]),
                  (10, 70))

        self.blit(font.render(f'{self.engine.hero.hp}/{self.engine.hero.max_hp}', True, colors["black"]),
                  (60, 30))
        self.blit(font.render(f'{self.engine.hero.exp}/{(100*(2**(self.engine.hero.level-1)))}', True, colors["black"]),
                  (60, 70))

        self.blit(font.render(f'Level', True, colors["black"]),
                  (300, 30))
        self.blit(font.render(f'Gold', True, colors["black"]),
                  (300, 70))

        self.blit(font.render(f'{self.engine.hero.level}', True, colors["black"]),
                  (360, 30))
        self.blit(font.render(f'{self.engine.hero.gold}', True, colors["black"]),
                  (360, 70))

        self.blit(font.render(f'Str', True, colors["black"]),
                  (420, 30))
        self.blit(font.render(f'Luck', True, colors["black"]),
                  (420, 70))

        self.blit(font.render(f'{self.engine.hero.stats["strength"]}', True, colors["black"]),
                  (480, 30))
        self.blit(font.render(f'{self.engine.hero.stats["luck"]}', True, colors["black"]),
                  (480, 70))

        self.blit(font.render(f'SCORE', True, colors["black"]),
                  (550, 30))
        self.blit(font.render(f'{self.engine.score:.4f}', True, colors["black"]),
                  (550, 70))
        # draw next surface in chain
        super().draw(canvas)


class InfoWindow(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.len = 30
        clear = []
        self.data = collections.deque(clear, maxlen=self.len)

    def update(self, value):
        self.data.append(f"> {str(value)}")

    def draw(self, canvas):
        self.fill(colors["wooden"])
        size = self.get_size()

        font = pygame.font.SysFont("comicsansms", 10)
        for i, text in enumerate(self.data):
            self.blit(font.render(text, True, colors["black"]),
                      (5, 20 + 18 * i))
        # FIXME
        # draw next surface in chain
        super().draw(canvas)


    def connect_engine(self, engine):
        # FIXME set this class as Observer to engine and send it to next in
        # chain
        engine.subscribe(self)
        super().connect_engine(engine)


class HelpWindow(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.len = 30
        clear = []
        self.data = collections.deque(clear, maxlen=self.len)
        self.data.append([" →", "Move Right"])
        self.data.append([" ←", "Move Left"])
        self.data.append([" ↑ ", "Move Top"])
        self.data.append([" ↓ ", "Move Bottom"])
        self.data.append([" H ", "Show Help"])
        self.data.append(["Num+", "Zoom +"])
        self.data.append(["Num-", "Zoom -"])
        self.data.append([" R ", "Restart Game"])
    # FIXME You can add some help information

    def connect_engine(self, engine):
        # FIXME save engine and send it to next in chain
        self.engine = engine
        super().connect_engine(engine)

    def draw(self, canvas):
        alpha = 0
        if self.engine.show_help:
            alpha = 128
        self.fill((0, 0, 0, alpha))
        size = self.get_size()
        font1 = pygame.font.SysFont("courier", 24)
        font2 = pygame.font.SysFont("serif", 24)
        if self.engine.show_help:
            pygame.draw.lines(self, (255, 0, 0, 255), True, [
                              (0, 0), (700, 0), (700, 500), (0, 500)], 5)
            for i, text in enumerate(self.data):
                self.blit(font1.render(text[0], True, ((128, 128, 255))),
                          (50, 50 + 30 * i))
                self.blit(font2.render(text[1], True, ((128, 128, 255))),
                          (150, 50 + 30 * i))

        # FIXME
        # draw next surface in chain
        super().draw(canvas)