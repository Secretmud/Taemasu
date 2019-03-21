

class Map:

    def __init__(self, map, width, height, pygame):
        self.map = open(map, 'r').readlines()
        self.width = width
        self.height = height
        self.square = 5
        self.rects = []
        # self.add_rects(pygame)

    def update(self, pygame, game_display):
        # print("update")
        self.draw_map(pygame, game_display)

    def can_use(self, rect1):
        rectlist = []
        for rect, color in self.rects:
            rectlist.append(rect)
        if rect1.collidelist(rectlist) == -1:
            return True
        return False

    def add_rects(self, pygame):
        blue = (0, 0, 255)
        white = (255, 255, 255)
        green = (0, 255, 0)
        number_y = 0
        for y in range(0, self.height, self.square):
            line = self.map[number_y].split(',')
            line.pop()
            number_x = 0
            if line.count('0') == len(line):
                number_y += 1
                continue

            for x in range(0, self.width, self.square):
                if line[number_x] == '1':
                    color = blue
                elif line[number_x] == '2':
                    color = green
                else:
                    number_x += 1
                    continue

                fill_rect = pygame.Rect(x, y, self.square, self.square)
                self.rects.append((fill_rect, color))
                number_x += 1
            number_y += 1

    def draw_map(self, pygame, game_display):
        for rect, color in self.rects:
            pygame.draw.rect(game_display, color, rect)


