import pygame
import os  # to define path to the images
from settings import *
import Game


class Runner(pygame.sprite.Sprite):  # Runner is a pygame Sprite object (Vererbung / Interface)
    def __init__(self):  # runs whenever a new object of this type is made
        pygame.sprite.Sprite.__init__(self)
        # a list that contains frames   & the frames are going to be the running

        self.sprites_running = []
        self.sprites_running.append(pygame.transform.scale(
            pygame.image.load(os.path.join('assets/Runner', 'runner1.png')), (RUNNER_WIDTH, RUNNER_HEIGHT)))
        self.sprites_running.append(pygame.transform.scale(
            pygame.image.load(os.path.join('assets/Runner', 'runner2.png')),  (RUNNER_WIDTH, RUNNER_HEIGHT)))
        self.sprites_running.append(pygame.transform.scale(
            pygame.image.load(os.path.join('assets/Runner', 'runner3.png')),  (RUNNER_WIDTH, RUNNER_HEIGHT)))
        self.sprites_running.append(pygame.transform.scale(
            pygame.image.load(os.path.join('assets/Runner', 'runner3a.png')),  (RUNNER_WIDTH, RUNNER_HEIGHT)))
        self.sprites_running.append(pygame.transform.scale(
            pygame.image.load(os.path.join('assets/Runner', 'runner4.png')),  (RUNNER_WIDTH, RUNNER_HEIGHT)))
        self.sprites_running.append(pygame.transform.scale(
            pygame.image.load(os.path.join('assets/Runner', 'runner5.png')),  (RUNNER_WIDTH, RUNNER_HEIGHT)))
        self.sprites_running.append(pygame.transform.scale(
            pygame.image.load(os.path.join('assets/Runner', 'runner6.png')),  (RUNNER_WIDTH, RUNNER_HEIGHT)))
        self.sprites_running.append(pygame.transform.scale(
            pygame.image.load(os.path.join('assets/Runner', 'runner7.png')),  (RUNNER_WIDTH, RUNNER_HEIGHT)))
        self.sprites_running.append(pygame.transform.scale(
            pygame.image.load(os.path.join('assets/Runner', 'runner8.png')),  (RUNNER_WIDTH, RUNNER_HEIGHT)))

        self.rect = pygame.Rect(MARGIN, HEIGHT - MARGIN - RUNNER_HEIGHT, RUNNER_WIDTH, RUNNER_HEIGHT)
       # runner_sprites = [None]*10
        #for picIndex in range(1, 10):
         #   runner_sprites[picIndex-1] = pygame.image.load(os.path.join("assets/Runner", "r" + str(picIndex) + ".png"))
          #  picIndex +=1

        self.index = 0 #stores the index of the current image


        self.VELOCITY_JUMP = 20
        self.jumping = False  # jetzt hier deklariert, damit ist der endlos jump gelöst

    def update(self):
        self.animate()

    def animate(self):
        clock = pygame.time.Clock()

        self.index += 1

        if self.index >= len(self.sprites_running): # geht alle Bilder durch (loop)
            self.index = 0 # will be reseted
        else:
            self.image = self.sprites_running[self.index] #the image that will be displayed
        clock.tick(70)

    def jump(self):
        self.rect.y -= self.VELOCITY_JUMP
        self.VELOCITY_JUMP -= 1
        if self.VELOCITY_JUMP < -20:
            self.jumping = False
            self.VELOCITY_JUMP = 20
