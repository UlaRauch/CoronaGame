import sys

import pygame
import os  # to define path to the images

from Mask import Mask
from PointsCounter import PointsCounter
from Superspreader import Superspreader
from settings import *
from Runner import Runner  # from filename import className
from Virus import Virus  # from filename import className
from Health import Health1, Health2, Health3

FPS = 60
FramePerSec = pygame.time.Clock()


class Game:
    def __init__(self):  # initialize game window etc
        self.game_over = None
        pygame.init()
        pygame.mixer.init()  # for sounds
        self.WIN = pygame.display.set_mode((WIDTH, HEIGHT))  # make new window of defined width & height
        pygame.display.set_caption(TITLE)  # window title
        self.clock = pygame.time.Clock()
        self.running = True
        self.playing = True
        self.pause = False
        self.click = False

        self.all_sprites = pygame.sprite.Group()  # creates new empty group for all sprites
        self.virus_group = pygame.sprite.Group()
        self.mask_group = pygame.sprite.Group()
        self.runner_group = pygame.sprite.Group()

        # create runner and add it to sprites group
        self.runner = None

        # all about virus creation
        self.superspreader = None  # use to produce virus and mask sprites
        # self.frame_counter = None  # use for intervals when producing new objects
        self.virus_counter = None  # used to measure player's progress and to set level
        self.virus_frequency = None
        self.mask_frequency = None

        # count collision -> virus
        self.collision_virus = 0

        # protection
        self.protected = False  # should be true for a certain period of time or frames after a mask has been collected
        self.protection_timer = None # count down when protected

        # count points (virus reached the left screen border)
        self.points_counter = None
        self.points = None  # equivalent to points earned during the game

        # heats for health
        self.health1 = None
        self.health2 = None
        self.health3 = None

        # level
        self.level = None

    def new(self):  # start a new game
        # create runner and add it to sprites group
        self.runner = Runner()
        self.all_sprites.add(self.runner)

        # initialize PointsCounter and points
        self.points_counter = PointsCounter()
        self.all_sprites.add(self.points_counter)
        self.points = 0  # points earned during the game

        # initialize health
        # create hearts and add them to sprites group
        self.health1 = Health1()
        self.health2 = Health2()
        self.health3 = Health3()
        self.all_sprites.add(self.health1)
        self.all_sprites.add(self.health2)
        self.all_sprites.add(self.health3)

        # protection
        self.protected = False  # should be true for a certain period of time or frames after a mask has been collected
        self.protection_timer = 0  # count down when protected

        # set counters to 0 (important when restarting the game)
        self.points = 0
        self.virus_counter = 0
        self.collision_virus = 0
        self.virus_frequency = 0
        self.mask_frequency = 0

        # self.frame_counter = 0  # use for intervals when producing new
        self.superspreader = Superspreader()

        # level
        self.level = 0

        self.running = True
        self.playing = True

        # run the game
        self.run()

    def run(self):  # code that handles main game loop in pygame
        MUSIC.play(loops=-1)  # play in endless loop
        while self.playing:  # game loop: open & close the window
            self.clock.tick(FPS)  # controls speed of the while loop
            self.events()
            self.update()
            self.draw()

    def update(self):  # game loop - update
        # virus sprite production depending on number of frames passed (virus_frequency is reduced with each frame in
        # superspreader)
        if self.virus_frequency == 0:  # self.frame_counter % self.virus_frequency == 0:
            virus = self.superspreader.produce_virus(self)  # produce virus with velocity 7
            self.all_sprites.add(virus)  # add virus to sprites group
            self.virus_group.add(virus)
            self.virus_counter += 1 #TODO: move to superspreader
            #self.frame_counter = 0 nicht mehr verwendet

        # increase level according to nr of produced viruses
        if self.virus_counter % 4 == 0:  # TODO: move modulus to settings?
            self.virus_counter = 1  # reset to 1 to prevent level from increasing with every frame
            self.level += 1
            print("changed level to: " + str(self.level))

        # count down protection timer
        if self.protected is True:
            self.protection_timer -= 1
            #print("protection timer: " + str(self.protection_timer))
            if self.protection_timer == 0:
                self.protected = False
                self.runner.runner_set_normal()
                print("end of protection")

        # mask production
        if self.level > 0:
            if self.mask_frequency == 0:  # self.level > 0 and self.virus_counter % 3 == 0:
                mask = self.superspreader.produce_mask(self)
                self.all_sprites.add(mask)
                self.mask_group.add(mask)
            self.mask_frequency -= 1  # count down interval between viruses

        # update sprites
        self.all_sprites.update()
        pygame.display.update()  # update changes
        self.virus_frequency -= 1

    def events(self):  # game loop - events
        for event in pygame.event.get():  # loop through list of all different events
            if event.type == pygame.QUIT:
                if self.playing:  # TODO: necessary?
                    self.playing = False  # end while loop if user quits game (press x)
                self.running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.click = True
        user_input = pygame.key.get_pressed()  # list of currently pressed key(s)
        if self.runner.jumping is False and user_input[pygame.K_SPACE]:
            self.runner.jumping = True
            JUMP_SOUND.play()  # muss an diese Stelle, überall anders wird der Ton verzerrt
        if self.runner.jumping:
            self.runner.jump()

        # detect collisions
        self.check_collision_with_mask()
        self.check_collision_with_virus()
        self.count_points()

    # collision with viruses
    # decrease health
    # end game
    def check_collision_with_virus(self):
        if pygame.sprite.spritecollide(self.runner, self.virus_group,
                                       True) and self.protected is False:
            self.collision_virus += 1
            COLLISION_SOUND.play()
            print(self.collision_virus)
            if self.collision_virus == 1:
                pygame.sprite.Sprite.kill(self.health3)

            elif self.collision_virus == 2:
                pygame.sprite.Sprite.kill(self.health2)
                self.runner.runner_set_almost_dead()  # make runner red when only 1 health is left

            elif self.collision_virus == 3:  # display_game_over hier aufrufen
                pygame.sprite.Sprite.kill(self.health1)
                print("you are  dead ")
                self.end_game()  # for a clean end
                s.display_name_screen()  # todo: only ask for name if highscore is achieved

    def check_collision_with_mask(self):
        if pygame.sprite.spritecollide(self.runner, self.mask_group, True):
            self.points += 5 # player earns 5 points for each mask
            self.runner.runner_set_protected()
            self.protected = True
            self.protection_timer = 100
            print("you are wearing a mask now")

    def count_points(self):  # detect and kill escaped viruses with the help of points_counter sprite object
        if pygame.sprite.spritecollide(self.points_counter, self.virus_group, True):
            self.points += 1
            print("Viruses escaped: " + str(self.points))
            print("Viruses in group: " + str(self.virus_group))

    def end_game(self):  # kill all remaining game objects
        self.playing = False  # game might be still running but not actively playing
        for thing in self.all_sprites:  # kills all sprites in the game! all sprites have to be initialized again with new game!
            thing.kill()

    def draw(self):  # game loop - draw
        self.WIN.fill(WHITE)  # RGB color for the window background, defined as constant
        # coordinate system: (0,0) is top left

        # uncommented because included in all_sprites group:
        # self.WIN.blit(self.runner.image,
        #              (self.runner.rect.x, self.runner.rect.y))  # draw surface (pictures, text, ...) on the screen
        # self.WIN.blit(self.virus.image,
        #              (self.virus.rect.x, self.virus.rect.y))
        self.all_sprites.draw(self.WIN)
        # start and stop button
        mx, my = pygame.mouse.get_pos()
        stop_button = pygame.Rect(WIDTH - 2 * MARGIN - SMALL_BUTTON_WIDTH, MARGIN, SMALL_BUTTON_WIDTH,
                                  SMALL_BUTTON_HEIGHT)
        pause_button = pygame.Rect(WIDTH - 2 * MARGIN - SMALL_BUTTON_WIDTH, 2 * MARGIN + SMALL_BUTTON_HEIGHT,
                                   SMALL_BUTTON_WIDTH, SMALL_BUTTON_HEIGHT)
        pygame.draw.rect(self.WIN, GREY, stop_button)
        pygame.draw.rect(self.WIN, GREY, pause_button)
        Menu.draw_text(self, "stop", pygame.font.Font(None, 50), BLACK, self.WIN, WIDTH - MARGIN - SMALL_BUTTON_WIDTH,
                       2 * MARGIN)
        Menu.draw_text(self, "pause", pygame.font.Font(None, 50), BLACK, self.WIN, WIDTH - MARGIN - SMALL_BUTTON_WIDTH,
                       3 * MARGIN + SMALL_BUTTON_HEIGHT)

        if stop_button.collidepoint(mx, my):
            if self.click:
                self.click = False
                # self.playing = False  - moved to end_game()
                self.end_game()  # kills all virus objects produced so far
                s.display_main_menu()
        if pause_button.collidepoint(mx, my):
            if self.click:
                self.click = False
                self.pause = True
                while self.pause:
                    s.display_pause_screen()

        # display points during the game
        text = "Points: " + str(self.points)
        Menu.draw_text(self, text, pygame.font.Font(None, 50), BLACK, self.WIN, 400, 2 * MARGIN)


class Menu:
    def __init__(self):  # initialize game window etc
        pygame.init()
        pygame.mixer.init()
        self.WIN = pygame.display.set_mode((WIDTH, HEIGHT))  # make new window of defined width & height
        pygame.display.set_caption(TITLE_START)  # window title
        self.running = True
        self.clock = pygame.time.Clock()
        self.font_very_small = pygame.font.Font(None, 25)
        self.font_small = pygame.font.Font(None, 60)
        self.font_big = pygame.font.Font(None, 100)
        self.click = False
        self.user_name = ""
        self.lines = []
        self.highscore = "0"
        self.highscore2 = "0"
        self.highscore3 = "0"

    def run(self):
        self.click = False
        pygame.display.update()
        self.clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.click = True

    def draw_text(self, text, font, color, surface, x, y):
        text_obj = font.render(text, 1, color)
        text_rect = text_obj.get_rect()
        text_rect.topleft = (x, y)
        surface.blit(text_obj, text_rect)

    def display_main_menu(self):
        while self.running:
            if MUSIC.play(): MUSIC.stop()
            self.WIN.fill(WHITE)
            mx, my = pygame.mouse.get_pos()
            # create buttons
            start_button = pygame.Rect(BUTTON1)
            highscore_button = pygame.Rect(BUTTON2)
            quit_button = pygame.Rect(BUTTON3)
            # display rectangles
            pygame.draw.rect(self.WIN, GREY, start_button)
            pygame.draw.rect(self.WIN, GREY, highscore_button)
            pygame.draw.rect(self.WIN, GREY, quit_button)
            # create circle button
            help_button = pygame.draw.circle(self.WIN, GREY, (WIDTH - 2 * MARGIN - RADIUS, 2 * MARGIN + RADIUS),
                                             RADIUS)  # surface, color, center, radius
            # display text
            self.draw_text("Corona Game", self.font_big, BLACK, self.WIN, 220, 80)
            self.draw_text("Play", self.font_small, BLACK, self.WIN, WIDTH / 2 - BUTTON_WIDTH / 2 + 2 * MARGIN,
                           180 + MARGIN)
            self.draw_text("High Score", self.font_small, BLACK, self.WIN, WIDTH / 2 - BUTTON_WIDTH / 2 + 2 * MARGIN,
                           180 + 2 * MARGIN + BUTTON_HEIGHT)
            self.draw_text("Quit", self.font_small, BLACK, self.WIN, WIDTH / 2 - BUTTON_WIDTH / 2 + 2 * MARGIN,
                           180 + 3 * MARGIN + 2 * BUTTON_HEIGHT)
            self.draw_text("?", self.font_small, BLACK, self.WIN, help_button.x + MARGIN, help_button.y + MARGIN)
            # display pictures
            runner = pygame.transform.scale(pygame.image.load(os.path.join('assets/Runner', "runner3a.png")),
                                            (RUNNER_WIDTH * 1.5, RUNNER_HEIGHT * 1.5))
            small_virus = pygame.transform.scale(pygame.image.load(os.path.join('assets', "virus.png")),
                                                 (VIRUS_WIDTH, VIRUS_HEIGHT))
            big_virus = pygame.transform.scale(pygame.image.load(os.path.join('assets', "virus.png")),
                                               (VIRUS_WIDTH * 2, VIRUS_HEIGHT * 2))
            self.WIN.blit(runner, (WIDTH - 2 * MARGIN - RUNNER_WIDTH * 1.5,
                                   HEIGHT - 2 * MARGIN - RUNNER_HEIGHT * 1.5))  # draw surface (pictures, text, ...) on the screen
            self.WIN.blit(small_virus, (50, 350))
            self.WIN.blit(big_virus, (150, 200))

            if start_button.collidepoint((mx, my)):
                if self.click:
                    self.click = False  # reset to avoid zombie runner (continues running when dead if mouse stays in the same position)
                    while g.running:
                        g.new()
            if quit_button.collidepoint(mx, my):
                if self.click:
                    pygame.quit()
                    sys.exit()
            if highscore_button.collidepoint(mx, my):
                if self.click:
                    s.display_high_score()
                    pass
            if help_button.collidepoint(mx, my):
                if self.click:
                    s.display_help_page()
            self.run()

    def display_help_page(self):
        indentation = 8 * MARGIN
        line_spacing = 40
        text_topleft = 160
        button_width = BUTTON_WIDTH * 0.5
        while self.running:
            self.WIN.fill(WHITE)
            mx, my = pygame.mouse.get_pos()
            back_button = pygame.Rect(WIDTH/2 - button_width/2, HEIGHT - MARGIN - BUTTON_HEIGHT, BUTTON_WIDTH * 0.5, BUTTON_HEIGHT)
            pygame.draw.rect(self.WIN, GREY, back_button)
            self.draw_text("Back", self.font_small, BLACK, self.WIN, WIDTH/2 - 50, HEIGHT - BUTTON_HEIGHT)
            self.draw_text("Corona Game", self.font_big, BLACK, self.WIN, 220, 50)
            # jede Zeile in einen Befehl, falls jemand eine bessere Lösung hat bitte ändern
            self.draw_text("Avoid getting hit by a virus by jumping over it. To jump, press the -SPACE KEY-.",
                           self.font_very_small, BLACK, self.WIN, indentation, text_topleft)
            self.draw_text("If you dodge the virus, you earn one point and the game continues.",
                           self.font_very_small, BLACK, self.WIN, indentation, text_topleft+line_spacing)
            self.draw_text("If run into a virus, you get infected and your health is decreased.",
                           self.font_very_small, BLACK, self.WIN, indentation, text_topleft + (2 * line_spacing))
            self.draw_text("After three infections, the game is lost.",
                           self.font_very_small, BLACK, self.WIN, indentation, text_topleft + (3 * line_spacing))
            self.draw_text("Masks give you temporal protection against virus infection and you earn 5 points.",
                            self.font_very_small, BLACK, self.WIN, indentation, text_topleft + (4 * line_spacing))
            self.draw_text("As long as you are wearing a mask, you don't have to dodge the virus.",
                            self.font_very_small, BLACK, self.WIN, indentation, text_topleft + (5 * line_spacing))

            if back_button.collidepoint((mx, my)):
                if self.click:
                    self.click = False
                    s.display_main_menu()

            self.run()

    def display_pause_screen(self):
        while self.running:
            pygame.mixer.pause()
            self.WIN.fill(WHITE)
            mx, my = pygame.mouse.get_pos()
            continue_button = pygame.Rect(WIDTH / 2 - BUTTON_WIDTH / 2, HEIGHT / 2 - BUTTON_HEIGHT / 2, BUTTON_WIDTH,
                                          BUTTON_HEIGHT)
            pygame.draw.rect(self.WIN, GREY, continue_button)
            self.draw_text("Continue", self.font_small, BLACK, self.WIN, WIDTH / 2 - BUTTON_WIDTH / 2 + 2 * MARGIN,
                           HEIGHT / 2 - BUTTON_HEIGHT / 2 + MARGIN)

            if continue_button.collidepoint((mx, my)):
                if self.click:
                    self.click = False
                    g.pause = False
                    break
            self.run()
        pygame.mixer.unpause()

    def display_name_screen(self):
        MUSIC.stop()
        GAME_OVER_SOUND.play()

        while self.running:
            # initialize text and buttons
            self.WIN.fill(WHITE)
            mx, my = pygame.mouse.get_pos()
            ok_button = pygame.Rect(WIDTH / 2 - BUTTON_WIDTH * 0.4 / 2, 180 + 2 * MARGIN + 2 * BUTTON_HEIGHT,
                                    BUTTON_WIDTH * 0.4, BUTTON_HEIGHT)
            user_input_box = pygame.Rect(450, 240, BUTTON_WIDTH, BUTTON_HEIGHT)
            pygame.draw.rect(self.WIN, GREY, ok_button)
            pygame.draw.rect(self.WIN, GREY, user_input_box)
            self.draw_text("Ooops! You are dead :/", self.font_big, BLACK, self.WIN, 60, 40)
            self.draw_text("Viruses avoided: " + str(g.points), self.font_small, BLACK,
                           self.WIN, 250, 130)
            self.draw_text("Your name: ", self.font_small, BLACK, self.WIN, 200, 250)
            self.draw_text(self.user_name, self.font_small, BLACK, self.WIN, user_input_box.x + MARGIN, user_input_box.y + MARGIN)
            self.draw_text("OK", self.font_small, BLACK, self.WIN, ok_button.x + MARGIN, ok_button.y + MARGIN)

            keys = pygame.key.get_pressed()  # list of currently pressed key(s)
            if keys[pygame.K_RETURN]:
                self.user_name = self.user_name[:-1]  # get text input from 0 to -1 i.e. end
                s.display_game_over()
            elif keys[pygame.K_BACKSPACE]:
                if len(self.user_name) > 0:
                    self.user_name = self.user_name[:len(self.user_name) - 1]
            else:   # TODO
                for key in keys:
                    if keys[key]:
                        print("unicode: {key}")
                        #self.user_name += key.unicode

            """for event in pygame.event.get():  # loop through list of all different events
                if event.type == pygame.KEYDOWN:  # get user input  # todo: user input is only sometimes recognised
                    if event.key == pygame.K_RETURN:
                        self.user_name = self.user_name[:-1]    # get text input from 0 to -1 i.e. end
                        s.display_game_over()
                    elif event.key == pygame.K_BACKSPACE and len(self.user_name) > 0:
                        self.user_name = self.user_name[:len(self.user_name)-1]
                    else:
                        print("unicode: " + event.unicode)
                        self.user_name += event.unicode"""

            if ok_button.collidepoint(mx, my):
                if self.click:
                    self.click = False
                    s.display_game_over()

            """if user_input_box.collidepoint(mx, my):
                if self.click:
                    self.click = False
                    # todo: ask for user input
                    # todo: add user input to highscore file"""

            self.run()

    def display_game_over(self):
        # add points to highscore list
        file = open("highscore.txt", "a")  # a = append at end of file
        file.write(str(g.points) + " " + self.user_name + "\n")  # each entry is a new line
        file.close()

        while self.running:
            # initialize text and buttons
            self.WIN.fill(WHITE)
            mx, my = pygame.mouse.get_pos()
            play_again_button = pygame.Rect(BUTTON1)  # TODO: positionen von verbessern
            main_menu_button = pygame.Rect(BUTTON2)
            quit_button = pygame.Rect(BUTTON3)
            pygame.draw.rect(self.WIN, GREY, play_again_button)
            pygame.draw.rect(self.WIN, GREY, main_menu_button)
            pygame.draw.rect(self.WIN, GREY, quit_button)
            self.draw_text("You are still dead :/", self.font_big, BLACK, self.WIN, 150, 40)
            self.draw_text("Play again", self.font_small, BLACK, self.WIN, play_again_button.x + MARGIN,
                           play_again_button.y + MARGIN)
            self.draw_text("Main Menu", self.font_small, BLACK, self.WIN, main_menu_button.x + MARGIN,
                           main_menu_button.y + MARGIN)
            self.draw_text("Quit", self.font_small, BLACK, self.WIN, quit_button.x + MARGIN, quit_button.y + MARGIN)

            self.draw_text("Viruses avoided: " + str(g.points), self.font_small, BLACK,
                           self.WIN, 250, 130)

            if play_again_button.collidepoint(mx, my):
                if self.click:
                    self.click = False  # reset to avoid zombie runner (continues running when dead if mouse stays in the same position)
                    g.new()  # run a new game

            if quit_button.collidepoint(mx, my):
                if self.click:
                    print("quit button clicked")
                    pygame.quit()
                    sys.exit()

            if main_menu_button.collidepoint(mx, my):
                if self.click:
                    self.click = False
                    self.display_main_menu()

            self.run()

    def display_high_score(self):
        # get highscore list
        file = open("highscore.txt", "r")  # read from file
        self.lines = file.readlines()  # create list
        self.lines.sort(key=lambda la: float(la.split(" ")[0]), reverse=True)  # sort points in descending order
        print(self.lines)
        self.highscore = self.lines[0]
        self.highscore2 = self.lines[1]
        self.highscore3 = self.lines[2]
        l = len(self.highscore)
        l2 = len(self.highscore2)
        l3 = len(self.highscore3)
        file.close()

        while self.running:
            self.WIN.fill(WHITE)
            mx, my = pygame.mouse.get_pos()
            button_width = BUTTON_WIDTH * 0.5
            self.draw_text("High Score", self.font_big, BLACK, self.WIN, 270, 80)
            self.draw_text(self.highscore[:l-1], self.font_small, BLACK, self.WIN, 350, 200)
            self.draw_text(self.highscore2[:l2-1], self.font_small, BLACK, self.WIN, 350, 250)
            self.draw_text(self.highscore3[:l3-1], self.font_small, BLACK, self.WIN, 350, 300)
            #back_button = pygame.Rect(MARGIN, HEIGHT - MARGIN - BUTTON_HEIGHT, BUTTON_WIDTH * 0.75, BUTTON_HEIGHT)
            back_button = pygame.Rect(WIDTH / 2 - button_width / 2, HEIGHT - MARGIN - BUTTON_HEIGHT, button_width,
                                      BUTTON_HEIGHT)
            pygame.draw.rect(self.WIN, GREY, back_button)
            self.draw_text("Back", self.font_small, BLACK, self.WIN, WIDTH/2 - 50, HEIGHT - BUTTON_HEIGHT)

            if back_button.collidepoint((mx, my)):
                if self.click:
                    self.click = False
                    s.display_main_menu()

            self.run()


g = Game()
s = Menu()
while s.running:
    s.display_main_menu()
