import numpy as np
import math
from math import *
import random
import time

class Player:
    def __init__(self, hp, attack, max_hp, x_bounds, y_bounds, health_bar, pygame):
        self.x_position = 150
        self.y_position = 150
        self.speed = 10
        self.max_speed = 10
        self.attack = attack
        self.hp = hp
        self.max_hp = max_hp
        self.playerImg = None
        self.current_x_speed = 0
        self.current_y_speed = 0
        self.x_bounds = x_bounds
        self.y_bounds = y_bounds
        self.picture_size = None
        self.health_bar = health_bar
        self.health_bar_size = health_bar.get_rect().size
        self.health_bar_border = 3
        self.stun_time = 5
        self.current_stun_time = 0
        self.stunned = False
        self.is_hitting_enemy = False
        self.fire_beam = pygame.image.load('firebeam.png')
        self.sucking_beam = pygame.image.load('sugingbeam.png')
        self.angle = 0
        self.mouse = False
        self.right_mouse = False 
        self.sucking_time = 5
        self.last_suck_time = 0
        self.can_suck_now = True
        self.type = 0

        self.load_image("player_player_def.png", pygame, "firebeam.png")

    def update(self, game_display, pygame, map, enemies):
        if ((self.x_bounds - self.picture_size[0] > self.x_position and self.current_x_speed > 0) or
                (self.x_position > 27 > self.current_x_speed + 27)):
            self.x_position += self.current_x_speed

        if((self.y_bounds - self.picture_size[1] > self.y_position and self.current_y_speed > 0) or
           (self.y_position > 27 > self.current_y_speed + 27)):
            self.y_position += self.current_y_speed

        if not map.can_use(pygame.Rect(self.x_position, self.y_position, self.picture_size[0], self.picture_size[1])):
            self.x_position -= self.current_x_speed
            self.y_position -= self.current_y_speed

        collides_with_enemies, enemy = self.collides_with(enemies, pygame)

        if collides_with_enemies and not self.is_hitting_enemy:
            self.playerImg.set_alpha(128)
            self.stunned = True
            # self.speed = self.speed / 3
            self.is_hitting_enemy = True
            self.hp = self.hp - enemy.damage

        if self.stunned:
            if self.current_stun_time < self.stun_time:
                self.current_stun_time += 1
            else:
                self.stunned = False
                self.current_stun_time = 0
                self.speed = self.max_speed
                self.playerImg.set_alpha(255)
                self.is_hitting_enemy = False

        game_display.blit(self.playerImg, (self.x_position, self.y_position))
        game_display.blit(self.health_bar, (self.x_position, self.y_position - self.health_bar_size[1]))

        self.draw_health_bar(game_display,
                             self.health_bar_size[1] - (2 * self.health_bar_border),
                             self.health_bar_size[0] - (2 * self.health_bar_border),
                             self.x_position + self.health_bar_border,
                             self.y_position - self.health_bar_size[1] + self.health_bar_border,
                             self.hp, self.max_hp, pygame)

        self.draw_fire(game_display, pygame, enemies)
        self.draw_sucking(game_display, pygame, enemies)

    def draw_health_bar(self, game_display, hp_bar_height, hp_bar_width, x, y, hp, max_hp, pygame):
        if hp <= 0:
            return
        green = (0, 255, 0)
        fill = int(max(min(hp / float(max_hp) * hp_bar_width, hp_bar_width), 0))
        fill_rect = pygame.Rect(x, y, fill, hp_bar_height)
        pygame.draw.rect(game_display, green, fill_rect)

    def collides_with(self, enemies, pygame):
        enemy_list = []
        for enemy in enemies:
            new_enemy = pygame.Rect(enemy.x_position, enemy.y_position, 30, 30)
            enemy_list.append(new_enemy)

        enemy_number = pygame.Rect(self.x_position, self.y_position, self.picture_size[0],
                                   self.picture_size[1]).collidelist(enemy_list)

        if not enemy_number == -1:
            return True, enemies[enemy_number]
        return False, None

    def get_key(self, event, pygame, game_display, enemies):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.current_x_speed = -self.speed
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.current_x_speed = self.speed
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                self.current_y_speed = -self.speed
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.current_y_speed = self.speed

        if event.type == pygame.KEYUP:
            if (event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT) or (event.key == pygame.K_a or event.key == pygame.K_d):
                self.current_x_speed = 0
            elif (event.key == pygame.K_UP or event.key == pygame.K_DOWN) or (event.key == pygame.K_s or event.key == pygame.K_w):
                self.current_y_speed = 0

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if pygame.mouse.get_pressed()[2] == 1:
                    self.mouse = False
                    self.right_mouse = False
                    return

                self.mouse = True
                self.draw_fire(game_display, pygame, enemies)

            if event.button == 3:
                if pygame.mouse.get_pressed()[0] == 1:
                    self.mouse = False
                    self.right_mouse = False
                    return

                self.right_mouse = True
                if self.can_suck_now:
                    self.draw_sucking(game_display, pygame, enemies)
                    self.last_suck_time = time.time()
                    # self.can_suck_now = False
                else:
                    if time.time() > self.last_suck_time + self.sucking_time:
                        self.can_suck_now = True

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.mouse = False
            elif event.button == 3:
                # print("right")
                self.right_mouse = False
                self.can_suck_now = False

    def xp_needed(self, xp, level):
        return ceil(100*(level/1.15))
    
    def level_up_hp(self, heal):
        hp_low = heal-5
        hp_high = heal+5
        new_hp = random.randrange(int(hp_low), int(hp_high))
        print(self.hp)
        self.max_hp = heal
        if self.hp > self.max_hp:
            self.hp = self.max_hp
        else:
            self.hp = new_hp
        # print(self.hp, self.max_hp)

    def hp(self):
        return self.hp

    def increase_hp(self, hp):
        new_hp = self.hp + hp
        if new_hp > self.max_hp:
            self.hp = self.max_hp
        else:
            self.hp = new_hp

    def increase_attack(self, attack):
        self.attack += attack

    def max_hp(self):
        return self.max_hp

    def get_hp(self, level):
        return ceil(level*1.2+level*sqrt(level*(level/4)) + 10)

    def draw_fire(self, game_display, pygame, enemies):
        if self.mouse:
            pos = pygame.mouse.get_pos()
            self.angle = 360 - math.atan2(pos[1] - self.y_position, pos[0] - self.x_position) * 180 / math.pi

            rotimage = pygame.transform.rotate(self.fire_beam, self.angle)
            rect = rotimage.get_rect(center=(self.x_position + self.picture_size[0] / 2,
                                             self.y_position + self.picture_size[1] / 2))
            game_display.blit(rotimage, rect)

            was_hit, enemies2 = self.attack_hits(enemies, pygame, rect, pos)
            if was_hit:
                for enemy in enemies2:
                    if enemy.type != self.type:
                        if self.type == 0 and enemy.type == 2:
                            enemy.takeDamage(self.attack * 0.1)
                        elif self.type == 0 and enemy.type == 3:
                            enemy.takeDamage(self.attack * 1.1)
                        elif self.type == 0 and enemy.type == 1:
                            enemy.takeDamage(self.attack * 0.1)
                        elif self.type == 1 and enemy.type == 0:
                            enemy.takeDamage(self.attack * 1.1)
                        elif self.type == 1 and enemy.type == 2:
                            enemy.takeDamage(self.attack * 0.1)
                        elif self.type == 1 and enemy.type == 3:
                            enemy.takeDamage(self.attack * -1)
                        elif self.type == 2 and enemy.type == 0:
                            enemy.takeDamage(self.attack * -1)
                        elif self.type == 2 and enemy.type == 1:
                            enemy.takeDamage(self.attack * 1.1)
                        elif self.type == 2 and enemy.type == 3:
                            enemy.takeDamage(self.attack * 0.1)
                        elif self.type == 3 and enemy.type == 1:
                            enemy.takeDamage(self.attack * 0.1)
                        elif self.type == 3 and enemy.type == 0:
                            enemy.takeDamage(self.attack * 0.1)
                        elif self.type == 3 and enemy.type == 2:
                            enemy.takeDamage(self.attack * 1.1)
                        else:
                            enemy.takeDamage(self.attack)

                        # enemy.takeDamage(self.attack)

    def attack_hits(self, enemies, pygame, rect, mouse_position):
        enemy_list = []
        for enemy in enemies:
            new_enemy = pygame.Rect(enemy.x_position, enemy.y_position, self.picture_size[0],
                                    self.picture_size[1])
            enemy_list.append(new_enemy)

        enemy_number = rect.collidelistall(enemy_list)
        new_enemy_list = []

        x = mouse_position[0] - self.x_position
        y = mouse_position[1] - self.y_position

        x_pluss = x > 0
        y_pluss = y > 0

        for number in enemy_number:
            new_enemy = enemies[number]
            x_enemy = self.x_position - new_enemy.x_position
            y_enemy = self.y_position - new_enemy.y_position

            x_pluss_enemy = x_enemy > 0
            y_pluss_enemy = y_enemy > 0

            if x_pluss != x_pluss_enemy and y_pluss != y_pluss_enemy:
                new_enemy_list.append(enemies[number])

        if len(enemy_number) > 0:
            return True, new_enemy_list
        return False, None

    def draw_sucking(self, game_display, pygame, enemies):
        if self.right_mouse:
            pos = pygame.mouse.get_pos()
            self.angle = 360 - math.atan2(pos[1] - self.y_position, pos[0] - self.x_position) * 180 / math.pi

            rotimage = pygame.transform.rotate(self.sucking_beam, self.angle)
            rect = rotimage.get_rect(center=(self.x_position + self.picture_size[0] / 2,
                                             self.y_position + self.picture_size[1] / 2))
            game_display.blit(rotimage, rect)

            was_hit, enemies2 = self.attack_hits(enemies, pygame, rect, pos)
            if was_hit:
                if enemies2 is not None and len(enemies2) > 0:
                    enemy = enemies2[random.randint(0, len(enemies2) - 1)]
                    self.set_type(enemy.type, pygame)
                    self.can_suck_now = False
                    # print(self.type)

    def can_suck(self):
        if time.time() > self.last_suck_time + self.sucking_time or time.time() < self.last_suck_time + 2:
            self.can_suck_now = True
            return True
        self.can_suck_now = False
        return False

    def angle_between(self, p1, p2):
        ang1 = np.arctan2(*p1[::-1])
        ang2 = np.arctan2(*p2[::-1])
        return np.rad2deg((ang1 - ang2) % (2 * np.pi))

    def set_type(self, damage_type, pygame):

        if damage_type == 0:
            self.load_image("player_player_fire.png", pygame, "firebeam.png")
        elif damage_type == 1:
            self.load_image("player_player_water.png", pygame, "waterbeam.png")
        elif damage_type == 2:
            self.load_image("player_player_wind.png", pygame, "windbeam.png")
        elif damage_type == 3:
            self.load_image("player_player_earth.png", pygame, "earthbeam.png")
        self.type = damage_type

    def load_image(self, image_name, pygame, beam_name):
        self.playerImg = pygame.image.load(image_name)
        self.playerImg = pygame.transform.scale(self.playerImg, (30, 50))
        self.picture_size = self.playerImg.get_rect().size
        self.fire_beam = pygame.image.load(beam_name)

    def load_image_large(self, image_name, pygame, beam_name):
        self.playerImg = pygame.image.load(image_name)
        self.playerImg = pygame.transform.scale(self.playerImg, (120, 200))
        self.picture_size = self.playerImg.get_rect().size
        self.fire_beam = pygame.image.load(beam_name)
