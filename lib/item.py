class Item:

    def __init__(self, location):
        self.location = location
        self.picked_up = False


class HealthBox(Item):

    def __init__(self, location, hp, pygame):
        Item.__init__(self, location)
        self.hp = hp
        self.image = pygame.image.load("lib/img/med-kit.png")
        self.type = 0



class AttackBoost(Item):

    def __init__(self, location, damage, pygame):
        Item.__init__(self, location)
        self.damage = damage
        self.image = pygame.image.load("lib/img/sword.png")
        self.type = 1

