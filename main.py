from math import sqrt, ceil
import pygame
from lib.player import Player
from lib.enemy import Enemy
import random
from lib.map import Map
from time import sleep
import threading
from lib.item import Item, HealthBox, AttackBoost
import sys

class Application:
    def __init__(self):
        pygame.init()
        displaySize = pygame.display.Info()
        self.display_width = 790
        self.display_height = 740
        self.level = 1
        self.xp = 1
        self.hp = 10
        self.max_hp = 10
        self.attack = 1
        self.talent_point = 0
        self.prev_level = 1
        self.is_paused = False
        pygame.display.set_caption('Taemasu v0.1')
        self.health_bar = pygame.image.load('lib/img/healthbar.png')
        self.player = Player(self.hp, self.attack, self.max_hp,
        self.display_width, self.display_height, self.health_bar, pygame)
        self.game_display = pygame.display.set_mode((displaySize.current_w, displaySize.current_h))
        self.white = (255, 255, 255)
        self.clock = pygame.time.Clock()
        self.crashed = False
        self.game_display.fill(self.white)
        self.enemies = []
        self.sword = pygame.image.load('lib/img/sword.png')
        self.map = Map('maptest.txt', self.display_width, self.display_height, pygame)
        pygame.font.init()  # you have to call this at the start,
        # if you want to use this module.
        self.myfont = pygame.font.SysFont('Comic Sans MS', 30)
        self.point = 0
        self.xp_new = 100 
        self.background = pygame.image.load('lib/img/background4.png')
        self.enemy_spawn_time = 2
        self.multiplier = 1
        self.start = True
        self.items = []
        self.exiting = False

        for count in range(0, 5):

            test_enemy = Enemy(random.randint(0, self.display_width), random.randint(0, self.display_height),
                               self.health_bar, pygame, self.multiplier)
            self.enemies.append(test_enemy)

        self.add_enemy()

    def main(self):
        while not self.crashed:
            if self.start:
                self.start_game()
            elif self.player.hp > 0:
                if self.exiting:
                    self.end_game()
                elif self.is_paused:
                    self.paused()
                else:
                    self.run_game()
            else:
                self.game_over()


            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()

    def run_game(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.crashed = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.is_paused = not self.is_paused
                elif event.key == pygame.K_ESCAPE:
                    self.exiting = True

            if not self.is_paused:
                self.player.get_key(event, pygame, self.game_display, self.enemies)

        # sleep(0.5)
        self.gui_update()
        # self.map.update(pygame, self.game_display)
        self.prev_level = self.level
        for enemy in self.enemies:
            enemy.update(self.game_display, self.player.x_position, self.player.y_position, pygame,
                         self.map, self.enemies)
            if enemy.is_dead():
                self.point += 1
                self.xp += ceil(self.level * 1.65 + 5 * sqrt(self.level))
                if enemy.will_drop_item():
                    if enemy.type == 0 or enemy.type == 3:
                        item = AttackBoost((enemy.x_position, enemy.y_position), 1, pygame)
                        self.items.append(item)
                    else:
                        item = HealthBox((enemy.x_position, enemy.y_position), 10, pygame)
                        self.items.append(item)
                self.enemies.remove(enemy)
                # enemy = None
                # del enemy

        if self.xp >= self.xp_new:
            self.level += 1
            self.xp = 0
            self.xp_new = self.player.xp_needed(self.xp, self.level)

        if self.level > self.prev_level:
            heal = self.player.get_hp(self.level)
            self.player.level_up_hp(heal)
            self.hp = self.player.hp
            self.enemy_spawn_time = self.enemy_spawn_time / 1.001

            self.multiplier = self.multiplier + 0.2

        self.hp = self.player.hp
        self.player.update(self.game_display, pygame, self.map, self.enemies)

        self.update_items()

    def update_items(self):

        new_item_list = []
        for item in self.items:
            if item.picked_up:
                self.items.remove(item)
            else:
                self.game_display.blit(item.image, item.location)
                new_item = pygame.Rect(item.location[0], item.location[1], 30, 40)
                new_item_list.append(new_item)

        item_numbers = pygame.Rect(self.player.x_position, self.player.y_position, self.player.picture_size[0],
                                   self.player.picture_size[1]).collidelistall(new_item_list)

        for number in item_numbers:
            item = self.items[number]
            if item.type == 0:
                self.player.increase_hp(item.hp)
            elif item.type == 1:
                self.player.increase_attack(item.damage)
            item.picked_up = True

    def game_over(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.crashed = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.reset()
        image = pygame.image.load("lib/img/gameover.png")
        # image = pygame.transform.scale(image, (790, 740))
        self.game_display.blit(image, (0, 0))

    def end_game(self):
        # drittspil
        image = pygame.image.load("lib/img/gameover.png")
        # image = pygame.transform.scale(image, (790, 740))
        self.game_display.blit(image, (0, 0))
        # self.is_paused = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.crashed = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    self.crashed = True
                elif event.key == pygame.K_n:
                    self.exiting = False




    def paused(self):
        image = pygame.image.load("lib/img/pause.png")
        # image = pygame.transform.scale(image, (790, 740))
        self.game_display.blit(image, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.crashed = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.is_paused = False



    def start_game(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.crashed = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.start = False
        image = pygame.image.load("lib/img/start.png")
        # image = pygame.transform.scale(image, (790, 740))
        self.game_display.blit(image, (0, 0))

    def reset(self):
        self.level = 1
        self.xp = 1
        self.hp = 10
        self.max_hp = 10
        self.attack = 1
        self.prev_level = 1
        self.player = Player(self.hp, self.attack, self.max_hp, self.display_width, self.display_height,
                             self.health_bar, pygame)
        self.crashed = False
        self.enemies = []
        self.point = 0
        self.xp_new = 100
        self.enemy_spawn_time = 5
        self.multiplier = 1
        self.items = []

        for count in range(0, 5):
            test_enemy = Enemy(random.randint(0, self.display_width), random.randint(0, self.display_height),
                               self.health_bar, pygame, self.multiplier)
            self.enemies.append(test_enemy)

        self.add_enemy()

    def add_enemy(self):
        threading.Timer(self.enemy_spawn_time, self.add_enemy).start()
        if not self.is_paused and not self.exiting:
            test_enemy = Enemy(random.randint(0, self.display_width),
                               random.randint(0, self.display_height), self.health_bar, pygame, self.multiplier)
            self.enemies.append(test_enemy)


    def gui_update(self):
        self.game_display.blit(self.background, (0, 0))
        points = self.myfont.render('Points: ' + str(self.point), False, (0, 0, 0))
        self.game_display.blit(points, (845, 40))
        level = self.myfont.render('Level:' + str(self.level), False, (0, 0, 0))
        self.game_display.blit(level, (845, 65))
        experience = self.myfont.render('Xp: ' + str(self.xp) + "/" +
                str(self.xp_new), False, (0, 0, 0))
        self.game_display.blit(experience, (845, 90))
        max_hp = self.myfont.render('Max HP: ' + str(self.player.max_hp), False, 
                                   (0, 0, 0))
        self.game_display.blit(max_hp, (845, 115))
        hp = self.myfont.render('HP:' + str(int(self.hp)), False, (0, 0, 0))
        self.game_display.blit(hp, (845, 145))
        #most_killed = self.game_display.blit(self.)
        player_damage = self.myfont.render('Player damage: ' + str(self.player.attack), False,
                                   (0, 0, 0))
        self.game_display.blit(player_damage, (845, 175))
        enemy_damage = self.myfont.render('Enemy damage: ' + 
                                          str(int(1 *self.multiplier)), False, 
                                          (0, 0, 0))
        self.game_display.blit(enemy_damage, (845, 205))
        image = pygame.transform.scale(self.player.playerImg, (120, 200))
        self.game_display.blit(image, (845, 300))

if __name__ == "__main__":
    main = Application()
    # main.add_enemy()
    main.main()
