# Plant Daddy
#
# Water all the plants, avoid the robots.
# Robots patrol.
# Player wins when all the plants are watered.
#
# Two classes:
# PlantDaddyApplication: start screen with title, how to play, user input to start game
# PlantDaddy: the game itself

import pygame

class PlantDaddy():
    def __init__(self):
        self.game_font = pygame.font.SysFont("couriernew", 17)
        self.shout_font = pygame.font.SysFont("Arial", 27)
        self.clock = pygame.time.Clock()

        self.load_images()
        self.set_grid()
        
        self.height = len(self.grid)
        self.width = len(self.grid[0])
        self.scale = 50
        self.window_height = self.scale * self.height
        self.window_width = self.scale * self.width
        self.window = pygame.display.set_mode((self.window_width, self.window_height + self.scale))

        # Initialize the best time to a very high number
        self.best_mins = 9999
        self.best_secs = 59
        self.best_millisecs = 9999

        with open("best_time.txt", "w") as results_file:
            results_file.write(f"{self.best_mins}:{self.best_secs:02}.{self.best_millisecs}")

        self.new_game()
        self.main_loop()

    def load_images(self):
        # Used chop to fit the images into a tile
        robot_image = pygame.image.load("robot.png")
        self.robot = pygame.transform.chop(robot_image, (45, 35, 30, 42))

        player_image = pygame.image.load("monster.png")
        self.player = pygame.transform.chop(player_image, (50, 45, 50, 50))

    def set_grid(self):
        # 0 - floor
        # 1 - wall
        # 2 - plant_happy
        # 3 - plant_sad
        # 4 - player (monster.png)
        # 5 - robot (robot.png)

        self.grid = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                     [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 3, 0, 0, 0, 0, 1],
                     [1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                     [1, 0, 5, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 5, 0, 0, 1],
                     [1, 0, 0, 0, 0, 0, 3, 1, 0, 0, 0, 0, 1, 0, 0, 3, 1],
                     [1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
                     [1, 3, 0, 0, 0, 0, 0, 1, 0, 0, 0, 3, 1, 0, 0, 0, 1],
                     [1, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 3, 1],
                     [1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 5, 0, 1, 1],
                     [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                     [1, 4, 0, 0, 0, 3, 0, 1, 3, 0, 0, 0, 0, 0, 0, 3, 1],
                     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

    def new_game(self):
        self.set_grid()
        self.plants_to_water()

        self.moves = 0
        self.game_over = False

        # This is used to regulate robot speed, see the move_robots function
        self.tick = 0

        # Reset the timer
        self.millisecs = 0
        self.secs = 0
        self.mins = 0

        # Used in calculate_timer to remember the start time of the current game
        self.reset = pygame.time.get_ticks()

        # robot velocities: top left, top right, bottom left, bottom right
        self.robot_tl = -1
        self.robot_tr = 1
        self.robot_bl = 1
        self.robot_br = -1

    def plants_to_water(self):
        self.plants_watered = 0
        self.total_plants = 0

        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == 3:
                    self.total_plants += 1

    def main_loop(self):
        while True:
            self.clock.tick(60)
            self.tick += 1

            self.calculate_timer()
            self.find_robots()
            self.check_events()
            self.draw_window()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.move(0, -1)
                if event.key == pygame.K_RIGHT:
                    self.move(0, 1)
                if event.key == pygame.K_UP:
                    self.move(-1, 0)
                if event.key == pygame.K_DOWN:
                    self.move(1, 0)
                if event.key == pygame.K_F2:
                    self.game_over = False
                    self.new_game()
                if event.key == pygame.K_ESCAPE:
                    exit()

            if event.type == pygame.QUIT:
                exit()

    def calculate_timer(self):
        if self.game_solved() or self.game_over:
            return
        
        ticks = pygame.time.get_ticks() - self.reset
        self.millisecs = ticks % 1000
        self.secs = int(ticks/1000 % 60)
        self.mins = int(ticks/60000 % 24)

    def find_robots(self):
        # Find all robots, put them in a list, send to move_robots
        robots_to_move = []

        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == 5:
                    robots_to_move.append((y, x))
                    
        self.move_robots(robots_to_move)

    def move_robots(self, robots_to_move: list):
        if self.game_solved() or self.game_over:
            return
        
        # Sets robot speed. 60 = one move per second
        if self.tick == 50:
            self.tick = 0

            for robot in robots_to_move:
                # top left robot
                if robot[1] == 2:
                    if self.grid[robot[0] + self.robot_tl][robot[1]] == 1:
                        self.robot_tl = -self.robot_tl

                    robot_new_y = robot[0] + self.robot_tl

                    if self.grid[robot_new_y][robot[1]] == 4:
                        self.game_over = True

                    self.grid[robot_new_y][robot[1]] = 5
                    self.grid[robot[0]][robot[1]] = 0
                
                # top right robot
                if robot[1] == 13 and robot[0] >= 1 and robot[0] <= 4:
                    if self.grid[robot[0] + self.robot_tr][robot[1]] == 1:
                        self.robot_tr = -self.robot_tr

                    robot_new_y = robot[0] + self.robot_tr

                    if self.grid[robot_new_y][robot[1]] == 4:
                        self.game_over = True

                    self.grid[robot_new_y][robot[1]] = 5
                    self.grid[robot[0]][robot[1]] = 0

                # bottom left robot
                if robot[1] == 4:
                    if self.grid[robot[0] + self.robot_bl][robot[1]] == 1:
                        self.robot_bl = -self.robot_bl

                    robot_new_y = robot[0] + self.robot_bl

                    if self.grid[robot_new_y][robot[1]] == 4:
                        self.game_over = True

                    self.grid[robot_new_y][robot[1]] = 5
                    self.grid[robot[0]][robot[1]] = 0

                # bottom right robot
                if robot[1] >= 8 and robot[1] <= 15 and robot[0] >= 6:
                    if self.grid[robot[0]][robot[1] + self.robot_br] == 1:
                        self.robot_br = -self.robot_br

                    robot_new_x = robot[1] + self.robot_br

                    if self.grid[robot[0]][robot_new_x] == 4:
                        self.game_over = True

                    self.grid[robot[0]][robot_new_x] = 5
                    self.grid[robot[0]][robot[1]] = 0

    def find_player(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == 4:
                    return (y, x)

    def move(self, move_y: int, move_x: int):
        if self.game_solved() or self.game_over:
            return

        player_old_y, player_old_x = self.find_player()
        player_new_y = player_old_y + move_y
        player_new_x = player_old_x + move_x

        # player hits a robot
        if self.grid[player_new_y][player_new_x] == 5:
            self.game_over = True
            return

        # player hits a wall
        if self.grid[player_new_y][player_new_x] == 1:
            return

        # player hits a happy plant
        if self.grid[player_new_y][player_new_x] == 2:
            return

        # player hits a sad plant
        if self.grid[player_new_y][player_new_x] == 3:
            self.grid[player_new_y][player_new_x] = 2
            self.plants_watered += 1
            return

        self.grid[player_old_y][player_old_x] -= 4
        self.grid[player_new_y][player_new_x] += 4

        self.moves += 1

    def game_solved(self):
        if self.plants_watered == self.total_plants:
            return True
        else:
            return False

    def draw_window(self):
        self.window.fill((240, 240, 240))

        # Draw the grid
        for y in range(self.height):
            for x in range(self.width):
                square = self.grid[y][x]

                # wall
                if square == 1:
                    self.window.fill((50, 50, 50), (x*self.scale+2, y*self.scale+2, 46, 46))

                # plant_happy
                if square == 2:
                    # pot
                    pygame.draw.polygon(self.window, (160, 82, 45),
                                        ((x*self.scale+6, y*self.scale+25),
                                         (x*self.scale+44, y*self.scale+25),
                                         (x*self.scale+40, y*self.scale+48),
                                         (x*self.scale+10, y*self.scale+48)))

                    # plant
                    pygame.draw.lines(self.window, (30, 205, 50), False,
                                      [(x*self.scale+20, y*self.scale+25),
                                       (x*self.scale+17, y*self.scale+20),
                                       (x*self.scale+15, y*self.scale+17),
                                       (x*self.scale+12, y*self.scale+5)], width=2)
                    pygame.draw.lines(self.window, (34, 139, 34), False,
                                      [(x*self.scale+23, y*self.scale+25),
                                       (x*self.scale+21, y*self.scale+21),
                                       (x*self.scale+19, y*self.scale+16),
                                       (x*self.scale+18, y*self.scale+1)], width=2)
                    pygame.draw.lines(self.window, (10, 160, 10), False,
                                      [(x*self.scale+25, y*self.scale+25),
                                       (x*self.scale+26, y*self.scale+20),
                                       (x*self.scale+23, y*self.scale+14),
                                       (x*self.scale+25, y*self.scale+3)], width=3)
                    pygame.draw.lines(self.window, (10, 180, 50), False,
                                      [(x*self.scale+30, y*self.scale+25),
                                       (x*self.scale+28, y*self.scale+17),
                                       (x*self.scale+30, y*self.scale+10),
                                       (x*self.scale+36, y*self.scale+2)], width=3)
                    pygame.draw.lines(self.window, (10, 200, 10), False,
                                      [(x*self.scale+28, y*self.scale+25),
                                       (x*self.scale+30, y*self.scale+19),
                                       (x*self.scale+32, y*self.scale+12),
                                       (x*self.scale+30, y*self.scale+2)], width=2)
                    pygame.draw.lines(self.window, (34, 139, 34), False,
                                      [(x*self.scale+26, y*self.scale+25),
                                       (x*self.scale+28, y*self.scale+15),
                                       (x*self.scale+30, y*self.scale+13),
                                       (x*self.scale+32, y*self.scale+1)], width=4)
                    pygame.draw.lines(self.window, (30, 205, 50), False,
                                      [(x*self.scale+33, y*self.scale+25),
                                       (x*self.scale+34, y*self.scale+20),
                                       (x*self.scale+35, y*self.scale+17),
                                       (x*self.scale+38, y*self.scale+5)], width=2)

                # plant_sad
                if square == 3:
                    # pot
                    pygame.draw.polygon(self.window, (160, 82, 45),
                                        ((x*self.scale+6, y*self.scale+25),
                                         (x*self.scale+44, y*self.scale+25),
                                         (x*self.scale+40, y*self.scale+48),
                                         (x*self.scale+10, y*self.scale+48)))

                    # plant
                    pygame.draw.lines(self.window, (250, 250, 0), False,
                                      [(x*self.scale+20, y*self.scale+25),
                                       (x*self.scale+15, y*self.scale+20),
                                       (x*self.scale+12, y*self.scale+30),
                                       (x*self.scale+10, y*self.scale+40)])
                    pygame.draw.lines(self.window, (210, 210, 0), False,
                                      [(x*self.scale+23, y*self.scale+25),
                                       (x*self.scale+19, y*self.scale+23),
                                       (x*self.scale+17, y*self.scale+28),
                                       (x*self.scale+15, y*self.scale+43)])
                    pygame.draw.lines(self.window, (190, 160, 30), False,
                                      [(x*self.scale+25, y*self.scale+25),
                                       (x*self.scale+24, y*self.scale+23),
                                       (x*self.scale+20, y*self.scale+32),
                                       (x*self.scale+23, y*self.scale+41)], width=2)
                    pygame.draw.lines(self.window, (200, 200, 20), False,
                                      [(x*self.scale+30, y*self.scale+25),
                                       (x*self.scale+33, y*self.scale+17),
                                       (x*self.scale+37, y*self.scale+30),
                                       (x*self.scale+38, y*self.scale+40)], width=2)
                    pygame.draw.lines(self.window, (173, 200, 47), False,
                                      [(x*self.scale+28, y*self.scale+25),
                                       (x*self.scale+30, y*self.scale+19),
                                       (x*self.scale+32, y*self.scale+32),
                                       (x*self.scale+32, y*self.scale+45)])
                    pygame.draw.lines(self.window, (173, 150, 17), False,
                                      [(x*self.scale+26, y*self.scale+25),
                                       (x*self.scale+28, y*self.scale+15),
                                       (x*self.scale+27, y*self.scale+33),
                                       (x*self.scale+28, y*self.scale+47)], width=2)

                # player
                if square == 4:
                    self.window.blit(self.player, (x*self.scale, y*self.scale))

                # robot
                if square == 5:
                    self.window.blit(self.robot, (x*self.scale, y*self.scale+3))

        # Define and display text on screen
        moves_text = self.game_font.render(f"Moves: {self.moves}", True, (0, 0, 0))
        plants_watered_text = self.game_font.render(f"Plants watered: {self.plants_watered}/{self.total_plants}", True, (0, 0, 0))
        new_game_text = self.game_font.render("F2: New game", True, (0, 0, 0))
        exit_game_text = self.game_font.render("ESC: Exit game", True, (0, 0, 0))
        timer_text = self.game_font.render(f"{self.mins}:{self.secs:02}", True, (0, 0, 0))

        self.window.blit(moves_text, (25, self.height*self.scale+7))
        self.window.blit(plants_watered_text, (25, self.height*self.scale+25))
        self.window.blit(new_game_text, (self.width*self.scale-150, self.height*self.scale+7))
        self.window.blit(exit_game_text, (self.width*self.scale-150, self.height*self.scale+25))
        self.window.blit(timer_text, (self.window_width/2-timer_text.get_width()/2, self.height*self.scale+15))

        if self.game_solved():
            # Display win text with a background so it's easier to read
            win_text = self.shout_font.render("Congratulations! All the plants are watered!", True, (0, 250, 127))
            pygame.draw.rect(self.window, (50, 50, 50), ((self.width*self.scale)/2-win_text.get_width()/2, self.height*self.scale-self.scale+2, 500, 46))
            self.window.blit(win_text, ((self.width*self.scale)/2-win_text.get_width()/2, self.height*self.scale-self.scale+8))

            # Display finished time with a background that covers the timer
            finished_timer = self.game_font.render(f"{self.mins}:{self.secs:02}.{self.millisecs}", True, (0, 0, 0))
            pygame.draw.rect(self.window, (240, 240, 240), (self.window_width/2-finished_timer.get_width()/2, self.height*self.scale, 100, 50))
            self.window.blit(finished_timer, (self.window_width/2-finished_timer.get_width()/2, self.height*self.scale+15))

            # If it's the best time ever, write finished time to file
            if self.mins < self.best_mins:
                self.best_mins = self.mins
                self.best_secs = self.secs
                self.best_millisecs = self.millisecs
            elif self.mins == self.best_mins:
                if self.secs < self.best_secs:
                    self.best_mins = self.mins
                    self.best_secs = self.secs
                    self.best_millisecs = self.millisecs
                elif self.secs == self.best_secs:
                    if self.millisecs < self.best_millisecs:
                        self.best_mins = self.mins
                        self.best_secs = self.secs
                        self.best_millisecs = self.millisecs

            with open("best_time.txt", "w") as results_file:
                results_file.write(f"{self.best_mins}:{self.best_secs:02}.{self.best_millisecs}")

        if self.game_over:
            # Display lose text with a background so it's easier to read
            lose_text = self.shout_font.render("GAME OVER", True, (220, 20, 60))
            pygame.draw.rect(self.window, (50, 50, 50), (self.window_width/2-lose_text.get_width()/2, self.height*self.scale-self.scale+2, 200, 46))
            self.window.blit(lose_text, (self.window_width/2-lose_text.get_width()/2, self.height*self.scale-self.scale+8))

            # Display finished time with a background that covers the timer
            finished_timer = self.game_font.render(f"{self.mins}:{self.secs:02}.{self.millisecs}", True, (0, 0, 0))  
            pygame.draw.rect(self.window, (240, 240, 240), (self.window_width/2-finished_timer.get_width()/2, self.height*self.scale, 100, 50))           
            self.window.blit(finished_timer, (self.window_width/2-finished_timer.get_width()/2, self.height*self.scale+15))

        pygame.display.flip()


class PlantDaddyApplication():
    def __init__(self):
        pygame.init()

        self.load_images()

        pygame.display.set_caption("Plant Daddy")
        self.window = pygame.display.set_mode((17*50, 12*50))
        self.title_font = pygame.font.SysFont("None", 170)
        self.howto_font = pygame.font.SysFont("couriernew", 27)
        self.clock = pygame.time.Clock()

    def load_images(self):
        robot_image = pygame.image.load("robot.png")
        self.robot = pygame.transform.chop(robot_image, (45, 35, 30, 42))

    def menu_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    PlantDaddy()

            if event.type == pygame.QUIT:
                exit()

    def draw_art(self):
        # Re-drawing all the art from the PlantDaddy class.
        # I'm sure there is a more elegant solution for this.
        self.window.fill((240, 240, 240))

        # robots
        self.window.blit(self.robot, ((self.window.get_width()/2)-100, 410))
        self.window.blit(self.robot, ((self.window.get_width()/2)+50, 410))

        # sad_pot
        pygame.draw.polygon(self.window, (160, 82, 45),
                            (((self.window.get_width()/2)-55, 265),
                             ((self.window.get_width()/2)-93, 265),
                             ((self.window.get_width()/2)-89, 288),
                             ((self.window.get_width()/2)-59, 288)))
        
        # happy_pot
        pygame.draw.polygon(self.window, (160, 82, 45),
                            (((self.window.get_width()/2)+55, 265),
                             ((self.window.get_width()/2)+93, 265),
                             ((self.window.get_width()/2)+89, 288),
                             ((self.window.get_width()/2)+59, 288)))

        # sad_plant
        pygame.draw.lines(self.window, (250, 250, 0), False,
                          [((self.window.get_width()/2)-80, 265),
                           ((self.window.get_width()/2)-85, 260),
                           ((self.window.get_width()/2)-88, 270),
                           ((self.window.get_width()/2)-90, 280)])
        pygame.draw.lines(self.window, (210, 210, 0), False,
                          [((self.window.get_width()/2)-77, 265),
                           ((self.window.get_width()/2)-81, 263),
                           ((self.window.get_width()/2)-83, 266),
                           ((self.window.get_width()/2)-85, 283)])
        pygame.draw.lines(self.window, (190, 160, 30), False,
                          [((self.window.get_width()/2)-75, 265),
                           ((self.window.get_width()/2)-76, 263),
                           ((self.window.get_width()/2)-80, 272),
                           ((self.window.get_width()/2)-77, 281)], width=2)
        pygame.draw.lines(self.window, (200, 200, 20), False,
                          [((self.window.get_width()/2)-70, 265),
                           ((self.window.get_width()/2)-67, 257),
                           ((self.window.get_width()/2)-63, 270),
                           ((self.window.get_width()/2)-62, 280)], width=2)
        pygame.draw.lines(self.window, (173, 200, 47), False,
                          [((self.window.get_width()/2)-72, 265),
                           ((self.window.get_width()/2)-70, 259),
                           ((self.window.get_width()/2)-68, 272),
                           ((self.window.get_width()/2)-68, 285)])
        pygame.draw.lines(self.window, (173, 150, 17), False,
                          [((self.window.get_width()/2)-74, 265),
                           ((self.window.get_width()/2)-72, 255),
                           ((self.window.get_width()/2)-73, 273),
                           ((self.window.get_width()/2)-72, 287)], width=2)

        # happy_plant
        pygame.draw.lines(self.window, (30, 205, 50), False,
                          [((self.window.get_width()/2)+70, 265),
                           ((self.window.get_width()/2)+67, 260),
                           ((self.window.get_width()/2)+65, 257),
                           ((self.window.get_width()/2)+62, 245)], width=2)
        pygame.draw.lines(self.window, (34, 139, 34), False,
                          [((self.window.get_width()/2)+73, 265),
                           ((self.window.get_width()/2)+71, 261),
                           ((self.window.get_width()/2)+69, 256),
                           ((self.window.get_width()/2)+68, 244)], width=2)
        pygame.draw.lines(self.window, (10, 160, 10), False,
                          [((self.window.get_width()/2)+75, 265),
                           ((self.window.get_width()/2)+76, 260),
                           ((self.window.get_width()/2)+73, 254),
                           ((self.window.get_width()/2)+75, 243)], width=3)
        pygame.draw.lines(self.window, (10, 180, 50), False,
                          [((self.window.get_width()/2)+80, 265),
                           ((self.window.get_width()/2)+78, 257),
                           ((self.window.get_width()/2)+80, 250),
                           ((self.window.get_width()/2)+86, 243)], width=3)
        pygame.draw.lines(self.window, (10, 200, 10), False,
                          [((self.window.get_width()/2)+78, 265),
                           ((self.window.get_width()/2)+80, 259),
                           ((self.window.get_width()/2)+82, 253),
                           ((self.window.get_width()/2)+80, 243)], width=2)
        pygame.draw.lines(self.window, (34, 139, 34), False,
                          [((self.window.get_width()/2)+76, 265),
                           ((self.window.get_width()/2)+78, 255),
                           ((self.window.get_width()/2)+80, 253),
                           ((self.window.get_width()/2)+82, 241)], width=4)
        pygame.draw.lines(self.window, (30, 205, 50), False,
                          [((self.window.get_width()/2)+83, 265),
                           ((self.window.get_width()/2)+84, 260),
                           ((self.window.get_width()/2)+85, 257),
                           ((self.window.get_width()/2)+88, 245)], width=2)

    def draw_titles(self):
        title = self.title_font.render("Plant Daddy", True, (0, 120, 0))
        water_plants = self.howto_font.render("Water the plants", True, (10, 10, 10))
        avoid_robots = self.howto_font.render("Avoid the robots", True, (10, 10, 10))
        press_space = self.howto_font.render("Press SPACE to start", True, (10, 10, 10))
        
        self.window.blit(title, ((self.window.get_width()-title.get_width())/2, 40))
        self.window.blit(water_plants, ((self.window.get_width()-water_plants.get_width())/2, 190))
        self.window.blit(avoid_robots, ((self.window.get_width()-avoid_robots.get_width())/2, 350))
        self.window.blit(press_space, ((self.window.get_width()-press_space.get_width())/2, self.window.get_height()-press_space.get_height()-30))

    def execute(self):
        while True:
            self.clock.tick(60)

            self.draw_art()
            self.draw_titles()
            self.menu_events()

            pygame.display.flip()


def main():
    application = PlantDaddyApplication()
    application.execute()


main()