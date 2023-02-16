import pygame
import sys

pygame.init()
display = pygame.display.set_mode((400, 300))
BLACK = (255, 255, 255)


class FPS:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Verdana", 20)
        self.text = self.font.render(str(self.clock.get_fps()), True, BLACK)

    def render(self, display):
        self.text = self.font.render(str(round(self.clock.get_fps(), 2)), True,
                                     BLACK)
        display.blit(self.text, (200, 150))


fps = FPS()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    display.fill((0, 0, 0))

    fps.render(display)

    pygame.display.update()
    fps.clock.tick(60)