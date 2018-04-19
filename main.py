# RPG Main Executable

import pygame as pg
import random
from os import path

from settings import *
from sprites import *
from keybinds import *


class Game:
    def __init__(self):
        # initialize game window, etc

        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        pg.display.set_caption(TITLE + " | FPS: " + str(int(self.clock.get_fps())))
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()

    def load_data(self):
        # Load HighScore
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, 'img')

        with open(path.join(self.dir, HS_FILE), 'w') as f:
            # Catch exception if file doesn't exist already
            try:
                self.highscore = int(f.read())
            # Self populate the HS to be 0
            except:
                self.highscore = 0

            self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))

    def new(self):
        # Restarts game / Start a new game
        self.score = 0
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.player = Player(self)
        self.all_sprites.add(self.player)

        for platform in PLATFORM_LIST:
            p = Platform(self, *platform)  # Take the list and explode it to list items
            self.all_sprites.add(p)
            self.platforms.add(p)

    def run(self):
        # game loop
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        # game loop - update
        self.all_sprites.update()
        print(str(int(self.clock.get_fps()))) # Display FPS in Console

        # Check if player hits a platform WHILE falling
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                self.player.pos.y = hits[0].rect.top + 1
                self.player.vel.y = 0

        # If player reaches top part of the screen (1/4) scroll platforms down
        if self.player.rect.top <= HEIGHT / 4:
            self.player.pos.y += max(abs(self.player.vel.y), 2)
            for platform in self.platforms:
                platform.rect.y += max(abs(self.player.vel.y), 2)

                # Unload platforms that are not in game windows. (Window HEIGHT + 20%)
                if platform.rect.top >= (HEIGHT * 1.20):
                    platform.kill()
                    self.score += random.randrange(5, 10)

        # Die condition
        if self.player.rect.bottom > HEIGHT:
            # Scroll the camera with the player
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()

        if len(self.platforms) == 0:
            self.playing = False

        # Spawn new platform to keep same avg of platforms
        while len(self.platforms) < 10:
            width = random.randrange(50, 100)
            p = Platform(self, random.randrange(0, WIDTH - width),  # Generate X spawn cords.
                         random.randrange(-75, -30))  # Generate Y spawn cords.
            self.all_sprites.add(p)
            self.platforms.add(p)

    def events(self):
        # Game Loop - events
        for event in pg.event.get():
            # check for closing the window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            # Jumping
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()

    def draw(self):
        # Game Loop - draw
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        self.screen.blit(self.player.image, self.player.rect)
        self.draw_text(str(self.score), 22, WHITE, WIDTH / 2, 15)

        pg.display.flip()

    def show_start_screen(self):
        # Game splash screen
        self.screen.fill(BGCOLOR)
        self.draw_text(TITLE, 50, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("ARROWS to Move. SPACE to Jump", 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press a key to play.", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        self.draw_text("High Score:" + str(self.highscore), 22, WHITE, WIDTH / 2, 15)
        pg.display.flip()
        self.wait_for_key()

    def show_gameover_screen(self):
        # Skip GameOver screen if "X" is pressed while playing
        if not self.running:
            return

        # Game over screen
        self.screen.fill(BGCOLOR)
        self.draw_text("GAME OVER", 50, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Score: " + str(self.score), 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press any key to play again.", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        # Check for new High Score.
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("You got a new HIGH SCORE: ", 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.score))
        else:
            self.draw_text("HIGH SCORE: " + str(self.highscore), 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)

        pg.display.flip()
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

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)


g = Game()
g.show_start_screen()
while g.running:
    g.new()  # Generates a new game
    g.run()  # Runs the game
    g.show_gameover_screen()

pg.quit()
