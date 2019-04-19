from lib.priority_queue import PriorityQueue
from collections import defaultdict
import random


class Enemy:
    def __init__(self, x_position, y_position, health_bar, pygame, multiplier):
        self.hp = 10 * multiplier
        self.max_hp = self.hp
        self.speed = 2 * multiplier
        self.current_x_speed = 0
        self.current_y_speed = 0
        self.damage = 1 * multiplier
        self.image = None
        self.picture_size = None
        self.x_position = x_position
        self.y_position = y_position
        self.health_bar = health_bar
        self.health_bar_size = health_bar.get_rect().size
        self.health_bar_border = 3
        self.last_x = x_position
        self.last_y = y_position
        self.stuck_counter = 0
        self.stuck_mode = False
        self.stuck_list = []
        self.type = 0
        self.set_type(pygame)
        self.stun_time = 5
        self.current_stun_time = 0
        self.stunned = False

    def set_type(self, pygame):
        new_type = random.randint(0, 3)
        self.type = new_type

        if new_type == 0:
            self.load_image("lib/img/enemy_fire.png", pygame)
        elif new_type == 1:
            self.load_image("lib/img/enemy_water.png", pygame)
        elif new_type == 2:
            self.load_image("lib/img/enemy_wind.png", pygame)
        elif new_type == 3:
            self.load_image("lib/img/enemy_earth.png", pygame)


    def load_image(self, image_name, pygame):
        self.image = pygame.image.load(image_name)
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.picture_size = self.image.get_rect().size

    def update(self, game_display, player_x, player_y, pygame, map, enemies):
        self.x_position, self.y_position = self.get_next_move(player_x, player_y, map, pygame, enemies)

        game_display.blit(self.image, (self.x_position, self.y_position))
        game_display.blit(self.health_bar, (self.x_position, self.y_position - self.health_bar_size[1]))
        self.draw_health_bar(game_display,
                             self.health_bar_size[1] - (2 * self.health_bar_border),
                             self.health_bar_size[0] - (2 * self.health_bar_border),
                             self.x_position + self.health_bar_border,
                             self.y_position - self.health_bar_size[1] + self.health_bar_border,
                             self.hp, self.max_hp, pygame)

    def draw_health_bar(self, game_display, hp_bar_height, hp_bar_width, x, y, hp, max_hp, pygame):
        if hp <= 0:
            return
        green = (0, 255, 0)
        fill = int(max(min(hp / float(max_hp) * hp_bar_width, hp_bar_width), 0))
        fill_rect = pygame.Rect(x, y, fill, hp_bar_height)
        pygame.draw.rect(game_display, green, fill_rect)

    def get_next_move(self, player_x, player_y, map, pygame, enemies):

        # return self.a_star(player_x, player_y, map, pygame, enemies)
        frontier = PriorityQueue()

        for x in range(0, int(self.speed)):
            for y in range(0, int(self.speed)):
                next = (self.x_position - x, self.y_position - y)
                priority = self.heuristic((player_x, player_y), next)
                frontier.put(next, priority)

                next = (self.x_position + x, self.y_position + y)
                priority = self.heuristic((player_x, player_y), next)
                frontier.put(next, priority)

                next = (self.x_position + x, self.y_position - y)
                priority = self.heuristic((player_x, player_y), next)
                frontier.put(next, priority)

                next = (self.x_position - x, self.y_position + y)
                priority = self.heuristic((player_x, player_y), next)
                frontier.put(next, priority)

        x, y = frontier.get()

        if self.stuck_mode:
            while True:
                number = str(x) + str(y)
                if not map.can_use(pygame.Rect(x, y, self.picture_size[0], self.picture_size[1])):
                    if frontier.size() > 0:
                        x, y = frontier.get()
                        continue

                if number in self.stuck_list:
                    x, y = frontier.get()
                    continue

                break

            # print(self.stuck_list)
            self.stuck_list.append(number)
            self.stuck_counter -= 1

            if self.stuck_counter == 0:
                self.stuck_mode = False
                self.stuck_list = []

            self.last_y = y
            self.last_x = x
            return x, y

        while not map.can_use(pygame.Rect(x, y, self.picture_size[0], self.picture_size[1])):
            x, y = frontier.get()

        # if not self.is_enemies_colliding(pygame.Rect(x, y, self.picture_size[0], self.picture_size[1]),
        #                                  enemies, pygame):
        #     self.last_x = self.x_position
        #     self.last_y = self.y_position
        #     return self.x_position, self.y_position

        if self.last_x == x and self.last_y == y and frontier.size() > 0:
            if map.can_use(pygame.Rect(x, y, self.picture_size[0], self.picture_size[1])):
                self.stuck_counter += 1

                if self.stuck_counter > 200:
                    self.stuck_mode = True

        self.last_x = x
        self.last_y = y
        return x, y

    def takeDamage(self, damage):
        if self.stunned:
            if self.current_stun_time < self.stun_time:
                self.current_stun_time += 1
            else:
                self.stunned = False
                self.current_stun_time = 0


        else:
            self.hp -= damage
            self.stunned = True

    def is_dead(self):
        if self.hp <= 0:
            return True
        return False

    def will_drop_item(self):
        number = random.randint(0, 100)
        if number > 95:
            return True

        return False

    def is_enemies_colliding(self, rect, enemies, pygame):
        enemy_list = []
        for enemy in enemies:
            new_enemy = pygame.Rect(enemy.x_position, enemy.y_position, self.picture_size[0], self.picture_size[1])
            enemy_list.append(new_enemy)

        collide = rect.collidelist(enemy_list)
        if collide == -1:
            return True
        x, y, z, k = enemy_list[collide]
        if x == self.x_position and y == self.y_position:
            return True
        return False


    def heuristic(self, a, b):
        (x1, y1) = a
        (x2, y2) = b

        return abs(x1 - x2) + abs(y1 - y2)

    def a_star(self, player_x, player_y, map, pygame, enemies):
        frontier = PriorityQueue()
        current = (self.x_position, self.y_position)
        priority = self.heuristic((player_x, player_y), current)
        frontier.put(current, priority, 0)

        i = 0
        while not self.is_goal(current, player_x, player_y):
            # print(i)
            for x in range(0, self.speed):
                for y in range(0, self.speed):
                    cost = x + y
                    next = (current[0] - x, current[0] - y)
                    priority = self.heuristic((player_x, player_y), next)
                    frontier.put(next, priority, cost)

                    next = (current[0] + x, current[0] + y)
                    priority = self.heuristic((player_x, player_y), next)
                    frontier.put(next, priority, cost)

                    next = (current[0] + x, current[0] - y)
                    priority = self.heuristic((player_x, player_y), next)
                    frontier.put(next, priority, cost)

                    next = (current[0] - x, current[0] + y)
                    priority = self.heuristic((player_x, player_y), next)
                    frontier.put(next, priority, cost)

            current = frontier.get()
            i += 1

        x, y = frontier.get()

        while not map.can_use(pygame.Rect(x, y, self.picture_size[0], self.picture_size[1])):
            x, y = frontier.get()

        if not self.is_enemies_colliding(pygame.Rect(x, y, self.picture_size[0], self.picture_size[1]),
                                         enemies, pygame):
            return self.x_position, self.y_position

        return x, y

    def is_goal(self, current, player_x, player_y):
        # print(abs(current[0] - player_x))
        if abs(current[0] - player_x) < 10 and abs(current[1] - player_y) < 10:
            return True

        return False
