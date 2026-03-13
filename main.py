import arcade
import random
import math
import sqlite3
import datetime

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Космический собиратель"

COLOR_BG = (0, 0, 0)
COLOR_SHIP_MAIN = (80, 85, 95)
COLOR_SHIP_DARK = (50, 55, 65)
COLOR_SHIP_LIGHT = (120, 125, 135)
COLOR_CYAN_BRIGHT = (0, 255, 255)
COLOR_CYAN_DARK = (0, 180, 180)
COLOR_CYAN_GLOW = (100, 255, 255)
COLOR_PURPLE = (75, 40, 90)
COLOR_ASTEROID = (128, 128, 128)
COLOR_ITEM = (255, 215, 0)
COLOR_TEXT = (255, 255, 255)
COLOR_BUTTON = (47, 79, 79)
COLOR_BUTTON_HOVER = (70, 130, 180)
COLOR_WHITE = (255, 255, 255)
COLOR_OVERLAY = (0, 0, 0, 180)

PLAYER_SPEED = 2.0
FRICTION = 0.98
ASTEROID_SPEED = 3
ITEMS_TO_WIN = 10
ASTEROID_SPAWN_RATE = 60


def init_db():
    conn = sqlite3.connect('game_results.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            score INTEGER,
            result TEXT
        )
    ''')
    conn.commit()
    conn.close()


def save_result(score, result_type):
    conn = sqlite3.connect('game_results.db')
    cursor = conn.cursor()
    date_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("INSERT INTO scores (date, score, result) VALUES (?, ?, ?)",
                   (date_now, score, result_type))
    conn.commit()
    conn.close()


def get_results():
    conn = sqlite3.connect('game_results.db')
    cursor = conn.cursor()
    cursor.execute("SELECT date, score, result FROM scores ORDER BY score DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()
    return rows



class Ship:
    def __init__(self):
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = SCREEN_HEIGHT / 2
        self.radius = 20
        self.change_x = 0
        self.change_y = 0
        self.angle = 0

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.change_x *= FRICTION
        self.change_y *= FRICTION
        self.center_x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.center_x))
        self.center_y = max(self.radius, min(SCREEN_HEIGHT - self.radius, self.center_y))

        if abs(self.change_x) > 0.01 or abs(self.change_y) > 0.01:
            self.angle = math.degrees(math.atan2(self.change_y, self.change_x)) + 90

    def draw(self):
        x = self.center_x
        y = self.center_y
        angle = self.angle

        def rotate_point(px, py, angle_deg, cx, cy):
            angle_rad = math.radians(angle_deg)
            dx = px - cx
            dy = py - cy
            new_x = cx + dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
            new_y = cy + dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
            return new_x, new_y

        left_wing = [
            rotate_point(x - 30, y, angle, x, y),
            rotate_point(x - 10, y + 7, angle, x, y),
            rotate_point(x - 10, y - 7, angle, x, y),
        ]
        arcade.draw_triangle_filled(*left_wing[0], *left_wing[1], *left_wing[2], COLOR_SHIP_DARK)

        left_wing_stripe = [
            rotate_point(x - 27, y, angle, x, y),
            rotate_point(x - 17, y + 4, angle, x, y),
            rotate_point(x - 17, y - 4, angle, x, y),
        ]
        arcade.draw_triangle_filled(*left_wing_stripe[0], *left_wing_stripe[1], *left_wing_stripe[2], COLOR_CYAN_DARK)

        right_wing = [
            rotate_point(x + 30, y, angle, x, y),
            rotate_point(x + 10, y + 7, angle, x, y),
            rotate_point(x + 10, y - 7, angle, x, y),
        ]
        arcade.draw_triangle_filled(*right_wing[0], *right_wing[1], *right_wing[2], COLOR_SHIP_DARK)

        right_wing_stripe = [
            rotate_point(x + 27, y, angle, x, y),
            rotate_point(x + 17, y + 4, angle, x, y),
            rotate_point(x + 17, y - 4, angle, x, y),
        ]
        arcade.draw_triangle_filled(*right_wing_stripe[0], *right_wing_stripe[1], *right_wing_stripe[2],
                                    COLOR_CYAN_DARK)

        body_points = [
            rotate_point(x, y + 23, angle, x, y),
            rotate_point(x + 13, y + 3, angle, x, y),
            rotate_point(x + 12, y - 17, angle, x, y),
            rotate_point(x, y - 10, angle, x, y),
            rotate_point(x - 12, y - 17, angle, x, y),
            rotate_point(x - 13, y + 3, angle, x, y),
        ]
        arcade.draw_polygon_filled(body_points, COLOR_SHIP_MAIN)

        left_side = [
            rotate_point(x - 13, y + 3, angle, x, y),
            rotate_point(x - 10, y + 17, angle, x, y),
            rotate_point(x - 7, y + 7, angle, x, y),
            rotate_point(x - 10, y - 3, angle, x, y),
        ]
        arcade.draw_polygon_filled(left_side, COLOR_SHIP_LIGHT)

        right_side = [
            rotate_point(x + 13, y + 3, angle, x, y),
            rotate_point(x + 10, y + 17, angle, x, y),
            rotate_point(x + 7, y + 7, angle, x, y),
            rotate_point(x + 10, y - 3, angle, x, y),
        ]
        arcade.draw_polygon_filled(right_side, COLOR_SHIP_LIGHT)

        center_stripe1 = [
            rotate_point(x - 3, y - 3, angle, x, y),
            rotate_point(x + 3, y - 3, angle, x, y),
            rotate_point(x + 3, y + 17, angle, x, y),
            rotate_point(x - 3, y + 17, angle, x, y),
        ]
        arcade.draw_polygon_filled(center_stripe1, COLOR_CYAN_BRIGHT)

        center_stripe2 = [
            rotate_point(x - 2, y - 15, angle, x, y),
            rotate_point(x + 2, y - 15, angle, x, y),
            rotate_point(x + 2, y - 5, angle, x, y),
            rotate_point(x - 2, y - 5, angle, x, y),
        ]
        arcade.draw_polygon_filled(center_stripe2, COLOR_CYAN_DARK)

        tower_base = [
            rotate_point(x - 5, y + 19, angle, x, y),
            rotate_point(x + 5, y + 19, angle, x, y),
            rotate_point(x + 4, y + 23, angle, x, y),
            rotate_point(x - 4, y + 23, angle, x, y),
        ]
        arcade.draw_polygon_filled(tower_base, COLOR_SHIP_DARK)

        tower_mid = [
            rotate_point(x - 3, y + 23, angle, x, y),
            rotate_point(x + 3, y + 23, angle, x, y),
            rotate_point(x + 3, y + 28, angle, x, y),
            rotate_point(x - 3, y + 28, angle, x, y),
        ]
        arcade.draw_polygon_filled(tower_mid, COLOR_SHIP_MAIN)

        tower_top = [
            rotate_point(x - 3, y + 27, angle, x, y),
            rotate_point(x + 3, y + 27, angle, x, y),
            rotate_point(x + 3, y + 31, angle, x, y),
            rotate_point(x - 3, y + 31, angle, x, y),
        ]
        arcade.draw_polygon_filled(tower_top, COLOR_CYAN_GLOW)

        ant_start = rotate_point(x, y + 31, angle, x, y)
        ant_end = rotate_point(x, y + 35, angle, x, y)
        arcade.draw_line(*ant_start, *ant_end, COLOR_CYAN_BRIGHT, 2)
        arcade.draw_circle_filled(*ant_end, 2, COLOR_CYAN_GLOW)

        left_ant_start = rotate_point(x - 12, y + 13, angle, x, y)
        left_ant_end = rotate_point(x - 15, y + 19, angle, x, y)
        arcade.draw_line(*left_ant_start, *left_ant_end, COLOR_CYAN_DARK, 2)
        arcade.draw_circle_filled(*left_ant_end, 1, COLOR_CYAN_BRIGHT)

        right_ant_start = rotate_point(x + 12, y + 13, angle, x, y)
        right_ant_end = rotate_point(x + 15, y + 19, angle, x, y)
        arcade.draw_line(*right_ant_start, *right_ant_end, COLOR_CYAN_DARK, 2)
        arcade.draw_circle_filled(*right_ant_end, 1, COLOR_CYAN_BRIGHT)

        left_leg = [
            rotate_point(x - 12, y - 13, angle, x, y),
            rotate_point(x - 8, y - 17, angle, x, y),
            rotate_point(x - 9, y - 30, angle, x, y),
            rotate_point(x - 11, y - 28, angle, x, y),
        ]
        arcade.draw_polygon_filled(left_leg, COLOR_PURPLE)
        leg_end_l = rotate_point(x - 9, y - 30, angle, x, y)
        leg_flame_l = rotate_point(x - 9, y - 33, angle, x, y)
        arcade.draw_line(*leg_end_l, *leg_flame_l, COLOR_CYAN_BRIGHT, 2)

        center_leg = [
            rotate_point(x - 3, y - 10, angle, x, y),
            rotate_point(x + 3, y - 10, angle, x, y),
            rotate_point(x + 2, y - 32, angle, x, y),
            rotate_point(x - 2, y - 32, angle, x, y),
        ]
        arcade.draw_polygon_filled(center_leg, COLOR_PURPLE)
        leg_end_c = rotate_point(x, y - 32, angle, x, y)
        leg_flame_c = rotate_point(x, y - 37, angle, x, y)
        arcade.draw_line(*leg_end_c, *leg_flame_c, COLOR_CYAN_BRIGHT, 3)

        right_leg = [
            rotate_point(x + 12, y - 13, angle, x, y),
            rotate_point(x + 8, y - 17, angle, x, y),
            rotate_point(x + 9, y - 30, angle, x, y),
            rotate_point(x + 11, y - 28, angle, x, y),
        ]
        arcade.draw_polygon_filled(right_leg, COLOR_PURPLE)
        leg_end_r = rotate_point(x + 9, y - 30, angle, x, y)
        leg_flame_r = rotate_point(x + 9, y - 33, angle, x, y)
        arcade.draw_line(*leg_end_r, *leg_flame_r, COLOR_CYAN_BRIGHT, 2)

        for i in range(3):
            p1 = rotate_point(x - 11, y + 10 - i * 5, angle, x, y)
            p2 = rotate_point(x + 11, y + 10 - i * 5, angle, x, y)
            arcade.draw_circle_filled(*p1, 1, COLOR_CYAN_BRIGHT)
            arcade.draw_circle_filled(*p2, 1, COLOR_CYAN_BRIGHT)

        arcade.draw_triangle_outline(*left_wing[0], *left_wing[1], *left_wing[2], COLOR_SHIP_LIGHT, 1)
        arcade.draw_triangle_outline(*right_wing[0], *right_wing[1], *right_wing[2], COLOR_SHIP_LIGHT, 1)

    def check_collision_with_asteroid(self, asteroid):
        ax = asteroid.center_x
        ay = asteroid.center_y
        ar = asteroid.radius

        def rotate_point(px, py, angle_deg, cx, cy):
            angle_rad = math.radians(angle_deg)
            dx = px - cx
            dy = py - cy
            new_x = cx + dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
            new_y = cy + dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
            return new_x, new_y

        collision_points = [
            (self.center_x, self.center_y, 12),
            (self.center_x, self.center_y + 15, 8),
            (self.center_x, self.center_y - 12, 8),
            (self.center_x - 25, self.center_y, 6),
            (self.center_x + 25, self.center_y, 6),
            (self.center_x - 15, self.center_y + 5, 5),
            (self.center_x - 15, self.center_y - 5, 5),
            (self.center_x + 15, self.center_y + 5, 5),
            (self.center_x + 15, self.center_y - 5, 5),
            (self.center_x, self.center_y + 25, 6),
            (self.center_x, self.center_y + 32, 4),
            (self.center_x - 14, self.center_y + 17, 4),
            (self.center_x + 14, self.center_y + 17, 4),
            (self.center_x - 10, self.center_y - 22, 5),
            (self.center_x - 9, self.center_y - 30, 4),
            (self.center_x + 10, self.center_y - 22, 5),
            (self.center_x + 9, self.center_y - 30, 4),
            (self.center_x, self.center_y - 25, 5),
            (self.center_x, self.center_y - 35, 4),
            (self.center_x - 10, self.center_y + 10, 5),
            (self.center_x + 10, self.center_y + 10, 5),
        ]

        for px, py, pr in collision_points:
            rx, ry = rotate_point(px, py, self.angle, self.center_x, self.center_y)
            dx = ax - rx
            dy = ay - ry
            distance = math.sqrt(dx * dx + dy * dy)
            if distance < (ar + pr):
                return True
        return False

    def collides_with_point(self, x, y):
        dx = self.center_x - x
        dy = self.center_y - y
        return math.sqrt(dx * dx + dy * dy) < 20
    def collides_with_point(self, x, y):
        dx = self.center_x - x
        dy = self.center_y - y
        return math.sqrt(dx * dx + dy * dy) < self.radius


class Asteroid:
    def __init__(self, player_x, player_y):
        self.center_x = random.choice([0, SCREEN_WIDTH])
        self.center_y = random.choice([0, SCREEN_HEIGHT])
        self.radius = 22
        angle = math.atan2(player_y - self.center_y, player_x - self.center_x)
        self.change_x = math.cos(angle) * ASTEROID_SPEED
        self.change_y = math.sin(angle) * ASTEROID_SPEED

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
        if (self.center_x < -50 or self.center_x > SCREEN_WIDTH + 50 or
                self.center_y < -50 or self.center_y > SCREEN_HEIGHT + 50):
            return False
        return True

    def draw(self):
        arcade.draw_circle_filled(self.center_x, self.center_y, self.radius, COLOR_ASTEROID)
        arcade.draw_circle_outline(self.center_x, self.center_y, self.radius, COLOR_WHITE, 2)

    def collides_with_point(self, x, y):
        dx = self.center_x - x
        dy = self.center_y - y
        return math.sqrt(dx * dx + dy * dy) < self.radius + 15


class Item:
    def __init__(self):
        self.center_x = random.randint(50, SCREEN_WIDTH - 50)
        self.center_y = random.randint(50, SCREEN_HEIGHT - 50)
        self.radius = 12
        self.collected = False

    def draw(self):
        if not self.collected:
            arcade.draw_circle_filled(self.center_x, self.center_y, self.radius, COLOR_ITEM)
            arcade.draw_circle_outline(self.center_x, self.center_y, self.radius, COLOR_WHITE, 2)

    def collides_with_point(self, x, y):
        if self.collected:
            return False
        dx = self.center_x - x
        dy = self.center_y - y
        return math.sqrt(dx * dx + dy * dy) < self.radius + 15


class Button:
    def __init__(self, center_x, center_y, width, height, text):
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, is_hover=False):
        color = COLOR_BUTTON_HOVER if is_hover else COLOR_BUTTON
        left = self.center_x - self.width / 2
        right = self.center_x + self.width / 2
        bottom = self.center_y - self.height / 2
        top = self.center_y + self.height / 2
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, color)
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, COLOR_WHITE, 2)
        arcade.draw_text(self.text, self.center_x, self.center_y, COLOR_TEXT,
                         font_size=18, anchor_x="center", anchor_y="center")

    def is_hovered(self, mouse_x, mouse_y):
        return (abs(mouse_x - self.center_x) <= self.width / 2 and
                abs(mouse_y - self.center_y) <= self.height / 2)


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(COLOR_BG)
        self.state = "MENU"
        self.ship = None
        self.asteroids = []
        self.items = []
        self.score = 0
        self.frame_count = 0
        self.game_result_text = ""
        self.mouse_x = 0
        self.mouse_y = 0

        self.btn_play = Button(400, 350, 200, 50, "ИГРАТЬ")
        self.btn_results = Button(400, 280, 200, 50, "МОИ РЕЗУЛЬТАТЫ")
        self.btn_back = Button(400, 100, 200, 50, "НАЗАД")
        self.btn_restart = Button(400, 200, 200, 50, "В МЕНЮ")
        init_db()

    def setup(self):
        self.ship = Ship()
        self.asteroids = []
        self.items = [Item() for _ in range(ITEMS_TO_WIN)]
        self.score = 0
        self.frame_count = 0

    def on_draw(self):
        self.clear()
        if self.state == "MENU":
            self.draw_menu()
        elif self.state == "PLAYING":
            self.draw_game()
        elif self.state == "GAME_OVER":
            self.draw_game_over()
        elif self.state == "RESULTS":
            self.draw_results()

    def draw_menu(self):
        arcade.draw_text("КОСМИЧЕСКИЙ СОБИРАТЕЛЬ", SCREEN_WIDTH // 2, 450,
                         COLOR_TEXT, font_size=24, anchor_x="center", bold=True)
        self.btn_play.draw(self.btn_play.is_hovered(self.mouse_x, self.mouse_y))
        self.btn_results.draw(self.btn_results.is_hovered(self.mouse_x, self.mouse_y))

    def draw_game(self):
        for item in self.items:
            item.draw()
        for asteroid in self.asteroids:
            asteroid.draw()
        self.ship.draw()
        arcade.draw_text(f"Собрано: {self.score}/{ITEMS_TO_WIN}", 10, SCREEN_HEIGHT - 30,
                         COLOR_TEXT, font_size=16, anchor_x="left")

    def draw_game_over(self):
        self.draw_game()
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, COLOR_OVERLAY)
        arcade.draw_text(self.game_result_text, SCREEN_WIDTH // 2, 400,
                         COLOR_TEXT, font_size=30, anchor_x="center", bold=True)
        arcade.draw_text(f"Счёт: {self.score}", SCREEN_WIDTH // 2, 350,
                         COLOR_TEXT, font_size=20, anchor_x="center")
        self.btn_restart.draw(self.btn_restart.is_hovered(self.mouse_x, self.mouse_y))

    def draw_results(self):
        arcade.draw_text("ТАБЛИЦА РЕЗУЛЬТАТОВ", SCREEN_WIDTH // 2, 550,
                         COLOR_TEXT, font_size=24, anchor_x="center")
        results = get_results()
        y = 450
        arcade.draw_text("Дата | Счёт | Результат", SCREEN_WIDTH // 2, y,
                         COLOR_TEXT, font_size=16, anchor_x="center")
        y -= 30
        for date, score, result in results:
            text = f"{date} | {score} | {result}"
            arcade.draw_text(text, SCREEN_WIDTH // 2, y, COLOR_TEXT,
                             font_size=14, anchor_x="center")
            y -= 25
        self.btn_back.draw(self.btn_back.is_hovered(self.mouse_x, self.mouse_y))

    def on_update(self, delta_time):
        if self.state != "PLAYING":
            return
        self.frame_count += 1
        self.ship.update()
        self.asteroids = [a for a in self.asteroids if a.update()]
        if self.frame_count % ASTEROID_SPAWN_RATE == 0:
            self.asteroids.append(Asteroid(self.ship.center_x, self.ship.center_y))

        for asteroid in self.asteroids:
            if self.ship.check_collision_with_asteroid(asteroid):
                self.end_game("ПОТРАЧЕНО", False)
                return

        for item in self.items:
            if not item.collected and item.collides_with_point(self.ship.center_x, self.ship.center_y):
                item.collected = True
                self.score += 1
        if self.score >= ITEMS_TO_WIN:
            self.end_game("ПОБЕДА!", True)

    def end_game(self, text, is_win):
        self.state = "GAME_OVER"
        self.game_result_text = text
        save_result(self.score, "WIN" if is_win else "LOSE")

    def on_key_press(self, key, modifiers):
        if self.state == "PLAYING":
            if key in (arcade.key.W, arcade.key.UP):
                self.ship.change_y += PLAYER_SPEED
            elif key in (arcade.key.S, arcade.key.DOWN):
                self.ship.change_y -= PLAYER_SPEED
            elif key in (arcade.key.A, arcade.key.LEFT):
                self.ship.change_x -= PLAYER_SPEED
            elif key in (arcade.key.D, arcade.key.RIGHT):
                self.ship.change_x += PLAYER_SPEED

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_press(self, x, y, button, modifiers):
        if self.state == "MENU":
            if self.btn_play.is_hovered(x, y):
                self.state = "PLAYING"
                self.setup()
            elif self.btn_results.is_hovered(x, y):
                self.state = "RESULTS"
        elif self.state == "GAME_OVER":
            if self.btn_restart.is_hovered(x, y):
                self.state = "MENU"
        elif self.state == "RESULTS":
            if self.btn_back.is_hovered(x, y):
                self.state = "MENU"


def main():
    init_db()
    game = MyGame()
    arcade.run()


if __name__ == "__main__":
    main()
