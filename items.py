import os
import sys

import pygame as pg
from PIL import Image
import random as rand

pg.init()
width, height = 800, 600
screen = pg.display.set_mode((width, height))

WHITE = (255, 255, 255)
BALL_COLOR = (255, 165, 0)
BALL_RADIUS = 15
FPS_LIMIT = 60
RENDER_TAIL = False
TIME_SPEED = 1


# pg.display.set_caption("My balls")


class GifSaver:
    """
    Класс, сохраняющий гифки
    """

    def __init__(self, directory, screen_width, screen_height):
        """
        Конструктор сохранялки гифок
        :param directory: путь к директории с результирующей гифкой
        :param screen_width: ширина экрана
        :param screen_height: высота экрана
        """
        self.gif_dir = directory
        self.res_gif_path = self.gif_dir + r"\res.gif"
        self.frames = []
        self.frames_count = 0
        self.size = (screen_width, screen_height)
        self.gif_num = 1

    def add_img(self, data):
        """
        Метод добавления кадра к гифке
        :param data: bytearray картинки
        """
        img = Image.frombytes("RGBA", self.size, data)
        self.frames_count += 1
        self.frames.append(img)

        if self.frames_count > 10:
            self.save_to_gif()

    def save_to_gif(self):
        """
        Метод сохранения гифки в директорию
        """
        self.frames[0].save(f"{self.gif_dir}\\part_gif{self.gif_num}.gif",
                            save_all=True,
                            append_images=self.frames[1:],
                            optimize=True,
                            duration=20,
                            loop=1)

        self.frames[0].close()
        self.frames.clear()
        self.frames_count = 0
        self.gif_num += 1

    def __del__(self):
        """
        Метод, вызываемый при удалении экземпляра GifSaver,
        закрывает все открытые доступы к temp гифкам и удаляет их,
        оставляя только результирующую гифку
        """
        gif_paths_list = list(map(lambda y: self.gif_dir + f"\\{y}",
                                  filter(lambda x: x.startswith("part_gif"),
                                         os.listdir(self.gif_dir))))
        gif_paths_list.sort(key=lambda x: int(x.split("\\")[-1][8:].split(".")[0]))
        gif_list = list(map(lambda x: Image.open(x), gif_paths_list))
        if not gif_list:
            return
        gif_list[0].save(self.res_gif_path,
                         save_all=True,
                         append_images=gif_list[1:],
                         optimize=True,
                         duration=20,
                         loop=0)
        for gif in gif_list:
            gif.close()
        for gif in gif_paths_list:
            os.remove(gif)
        print(f"Гифка сохранена по адресу {self.res_gif_path}")


class TextBlock:
    def __init__(self):
        self.clock = pg.time.Clock()
        self.font_size = 20
        self.font = pg.font.SysFont("Comic Sans", self.font_size)

    def render(self, display, text: list[str]):
        rendered_text = [
            self.font.render("FPS: " + str(round(self.clock.get_fps(), 2)),
                             True,
                             WHITE)]
        for line in text:
            rendered_text.append(self.font.render(line, True, WHITE))

        for pos_y, line in enumerate(rendered_text):
            display.blit(line, (10, (10 + self.font_size) * pos_y))

    def tick(self, fps):
        self.clock.tick(fps)


class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __len__(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y

    def __mul__(self, other):
        return Vec2(other * self.x, other * self.y)

    def __imul__(self, other):
        self.x *= other
        self.y *= other

    def __repr__(self):
        return f"Vec2(x={self.x}, y={self.y})"

    def invert_x(self):
        self.x = -self.x

    def invert_y(self):
        self.y = -self.y


class Box:
    def __init__(self, x=None, y=None, width=None, height=None, pos=None, size=None):
        if x is not None:
            self.x, self.y = x, y
            self.width, self.height = width, height
        if pos is not None:
            self.x, self.y = pos.x, pos.y
            self.width, self.height = size.x, size.y
        if not all((self.x, self.y, self.width, self.height)):
            raise ValueError("incorrect arguments")

    def get_right(self):
        return self.x + self.width

    def get_bot(self):
        return self.y + self.height

    def get_top_left(self):
        return Vec2(self.x, self.y)

    def get_center(self):
        return Vec2(self.x + self.width / 2, self.y + self.height / 2)

    def __contains__(self, box):
        return self.x <= box.x and \
               box.get_right() <= self.get_right() and \
               self.y <= box.y and \
               box.get_bot() <= self.get_bot()

    def intersects(self, box):
        return not (self.x >= box.get_right() or
                    self.get_right() <= box.x or
                    self.y >= box.get_bot() or
                    self.get_bot() <= box.y)


class Ball:
    def __init__(self, screen: pg.display,
                 pos_x: float,
                 pos_y: float,
                 velocity: Vec2):
        self.screen = screen
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.velocity = velocity
        self.max_x, self.max_y = self.screen.get_size()

    def move(self):

        self.pos_x += self.velocity.x * TIME_SPEED
        self.pos_y += self.velocity.y * TIME_SPEED

        if not BALL_RADIUS <= self.pos_x <= self.max_x - BALL_RADIUS:
            self.velocity.invert_x()

        if not BALL_RADIUS <= self.pos_y <= self.max_y - BALL_RADIUS:
            self.velocity.invert_y()
        self.render()

    def render_tail(self):
        tail_len = 10
        r, g, b = BALL_COLOR

        for i in range(tail_len, 0, -1):
            pg.draw.circle(self.screen,
                           (r - r // tail_len * i,
                            g - g // tail_len * i,
                            b - b // tail_len * i),
                           (self.pos_x - rand.uniform(1, 1.5) *
                            BALL_RADIUS * self.velocity.x / tail_len * i,
                            self.pos_y - rand.uniform(1, 1.5) *
                            BALL_RADIUS * self.velocity.y / tail_len * i),
                           BALL_RADIUS - BALL_RADIUS / tail_len * i)

    def render(self):

        if RENDER_TAIL:
            self.render_tail()
        pg.draw.circle(self.screen, BALL_COLOR, (self.pos_x, self.pos_y),
                       BALL_RADIUS)

    def __repr__(self):
        return f"Ball(({self.pos_x}, {self.pos_y}), speed={self.velocity})"

    def collide(self, other_ball):
        print(self, other_ball, "collided")


def generate_random_ball(click_pos=None):
    speed_coef = 5
    if click_pos:
        b_x, b_y = rand.randint(click_pos[0] - width // 10,
                                click_pos[0] + width // 10), \
                   rand.randint(click_pos[1] - height // 10,
                                click_pos[1] + height // 10)
    else:
        b_x, b_y = rand.randint(BALL_RADIUS, width - BALL_RADIUS), \
                   rand.randint(BALL_RADIUS, height - BALL_RADIUS)
    vel = Vec2(rand.uniform(-1, 1) * speed_coef, rand.uniform(-1, 1) * speed_coef)
    return Ball(screen, b_x, b_y, vel)


def main():
    global TIME_SPEED, RENDER_TAIL
    gifer = GifSaver("images", width, height)
    text_block = TextBlock()
    balls = []
    # for i in range(5):
    #     balls.append(generate_random_ball())

    is_recording = False

    start_pos = None, None
    finish_pos = None, None

    none_point = None, None
    do_time = True

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == pg.BUTTON_LEFT:
                    start_pos = event.pos
                if event.button == pg.BUTTON_RIGHT:
                    if balls:
                        balls.pop()

            if event.type == pg.MOUSEBUTTONUP:
                if event.button == pg.BUTTON_LEFT:
                    finish_pos = event.pos

            if event.type == pg.MOUSEWHEEL:
                TIME_SPEED += event.y / 10

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    is_recording = not is_recording
                if event.key == pg.K_f:
                    do_time = not do_time
                if event.key == pg.K_t:
                    RENDER_TAIL = not RENDER_TAIL

        if is_recording:
            gifer.add_img(pg.image.tostring(screen, "RGBA"))

        screen.fill((0, 0, 0))

        if start_pos != none_point and \
                finish_pos == none_point and \
                event.type != pg.WINDOWLEAVE:
            pg.draw.line(screen, BALL_COLOR, start_pos, event.pos)

        if start_pos != none_point and finish_pos != none_point:
            vel = Vec2((finish_pos[0] - start_pos[0]) / (width // 10),
                       (finish_pos[1] - start_pos[1]) / (height // 10))
            b_x, b_y = start_pos
            balls.append(Ball(screen, b_x, b_y, vel))

            start_pos, finish_pos = none_point, none_point

        if do_time:
            for ball in balls:
                ball.move()
        else:
            for ball in balls:
                ball.render()

        text_block.render(screen, [f"Balls count: {len(balls)}",
                                   f"Time speed: {TIME_SPEED:.1f}"])
        pg.display.update()
        text_block.tick(FPS_LIMIT)


if __name__ == '__main__':
    main()
