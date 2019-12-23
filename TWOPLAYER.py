from MAIN_FRAME import *

"""
________________________________________________________________________________________________________________________
Two Player Classes
________________________________________________________________________________________________________________________
"""


class Player2P(pygame.sprite.Sprite):
    def __init__(self, color, x, y, team):  # defines what the class should do/what traits it has at startup
        pygame.sprite.Sprite.__init__(self)  # needed to initialize the sprite
        # graphics
        self.image = pygame.Surface((UNIT_SIZE, UNIT_SIZE))
        self.image.fill(color)
        # convert into form pygame can manipulate
        # hitboxes
        self.rect = self.image.get_rect()  # sets hitbox
        self.radius = int(self.rect.width / 3)
        # pygame.draw.circle(self.image, YELLOW, self.rect.center, self.radius)
        self.rect.center = (x, y)  # sets position of rectangle
        self.speed_x = 0  # creates variable "speedx" for each instance of self (player)
        self.speed_y = 0
        self.fire_delay = 0
        self.r = 70
        self.theta = PI / 2

        self.team = team
        self.hp = 5

        self.aimx = self.rect.centerx + (self.r * math.cos(math.degrees(self.theta)))
        self.aimy = self.rect.centery + (self.r * math.sin(math.degrees(self.theta)))
        self.aim = Aim(color, self.rect.centerx + (self.aimx), self.rect.centery + (self.aimy))

    def update(self, up, down, left, right, anticlockwise_key, clockwise_key):
        self.speed_x = 0  # reset speed every frame
        self.speed_y = 0
        key_state = pygame.key.get_pressed()

        if key_state[up]:  # standard WASD movement
            self.move(0, -PLAYER_SPEED)
        if key_state[left]:
            self.move(-PLAYER_SPEED, 0)
        if key_state[down]:
            self.move(0, PLAYER_SPEED)
        if key_state[right]:
            self.move(PLAYER_SPEED, 0)
        if key_state[anticlockwise_key]:
            self.theta -= 0.0007
            # self.move_aim(anticlockwise)
        if key_state[clockwise_key]:
            self.theta += 0.0007
            # self.move_aim(clockwise)

        self.aimx = self.rect.centerx + (self.r * math.cos(math.degrees(self.theta)))
        self.aimy = self.rect.centery + (self.r * math.sin(math.degrees(self.theta)))
        self.aim.update(self.aimx, self.aimy)

        if self.rect.left > WIDTH:  # if reach edge
            self.rect.right = 0  # set the right side of sprite to be x position 0
        if self.rect.right < 0:
            self.rect.left = WIDTH
        if self.rect.top > HEIGHT:
            self.rect.bottom = 0
        if self.rect.bottom < 0:
            self.rect.top = HEIGHT

    def shoot(self):
        p_x = self.rect.centerx
        p_y = self.rect.centery
        theta2 = math.atan2((self.aim.rect.centery - p_y), (self.aim.rect.centerx - p_x))

        bit_x_dir = BIT_SPEED * math.cos(theta2)
        bit_y_dir = BIT_SPEED * math.sin(theta2)

        bit = Bit2P(self.rect.centerx, self.rect.centery, 1, bit_y_dir, bit_x_dir, self.team)
        game.ALL_SPRITES.add(bit)
        game.bullets.add(bit)

        if self.team == "RED":
            game.p1bullets.add(bit)
        if self.team == "BLUE":
            game.p2bullets.add(bit)

    def fire(self, time_since_last_fire):
        self.fire_delay += time_since_last_fire
        if self.fire_delay > PLAYER_FIRE_DELAY_2P:
            self.shoot()
            self.fire_delay = 0

    def move(self, speed_x, speed_y):
        """Needed the move and move_one_direction overwrites on this section because movement with the player works
        differently (no bounce, just stop)"""
        self.speed_y = speed_y
        self.speed_x = speed_x
        if speed_x != 0:
            self.move_one_direction(speed_x, 0)
        if speed_y != 0:
            self.move_one_direction(0, speed_y)

    def move_one_direction(self, speed_x, speed_y):
        """need to move one direction at a time so that when colliding with barricades, it won't create a bug where
        inputting both an x and y direction will teleport the player to the corner; for example, moving right and moving
        up, the player's x position and y position will be changed, and the player will be teleported to the bottom left
        hand corner, because both conditions are activated. However, we want the player to keep the same x position if
        he is moving up, and the same y position if he is moving down, which can't be achieved without one direction
        because operating on both positions will change both x and y. It's sort of like livelock.
        This collision method was made possible by https://www.pygame.org/project-Rect+Collision+Response-1061-.html"""

        self.rect.x += speed_x  # moves rect by speed_x
        self.rect.y += speed_y
        self.stop()

    def stop(self):
        for barricade in game.BARRICADES:
            if self.rect.colliderect(barricade.rect):  # detects collision with right side of barricade
                if self.speed_x > 0:  # Going right
                    self.rect.right = barricade.rect.left
                if self.speed_x < 0:  # Going left
                    self.rect.left = barricade.rect.right
                if self.speed_y > 0:  # Going down
                    self.rect.bottom = barricade.rect.top
                if self.speed_y < 0:  # Going up
                    self.rect.top = barricade.rect.bottom


class Aim(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        pygame.sprite.Sprite.__init__(self)  # needed to initialize the sprite
        self.image = pygame.Surface((AIM_SIZE, AIM_SIZE))  # draw rectangle
        self.image.fill(color)  # fill rectangle
        self.rect = self.image.get_rect()  # set hitbox
        self.rect.center = (x, y)

    def update(self, x, y):
        self.rect.center = (x, y)


class Bit2P(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, y_direction, x_direction, team):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((BIT_SIZE_2P, BIT_SIZE_2P))
        if team == "RED":
            self.image.fill(RED)
        elif team == "BLUE":
            self.image.fill(BLUE)

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.speed_y = y_direction * speed
        self.speed_x = x_direction * speed
        self.hp = 2

        self.team = team

    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.kill()

    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if self.rect.bottom < 0:
            self.hit()
            self.rect.bottom = 0
        if self.rect.top > HEIGHT:
            self.hit()
            self.rect.top = HEIGHT
        if self.rect.left >= WIDTH:
            self.hit()
            self.rect.left = WIDTH
        if self.rect.right <= 0:
            self.hit()
            self.rect.right = 0

        self.move(self.speed_x, self.speed_y)

    def move(self, speed_x, speed_y):
        if speed_x != 0:
            self.move_one_direction(speed_x, 0)
        if speed_y != 0:
            self.move_one_direction(0, speed_y)

    def move_one_direction(self, speed_x, speed_y):
        self.rect.x += speed_x
        self.bounce("x")
        self.rect.y += speed_y
        self.bounce("y")

    def bounce(self, direction):
        for barricade in game.BARRICADES:
            if self.rect.colliderect(barricade.rect):  # detects collision with right side of barricade
                if direction == "x":
                    if self.speed_x > 0:  # Going right
                        self.rect.right = barricade.rect.left
                        self.speed_x *= -1
                        self.hit()
                    elif self.speed_x < 0:  # Going left
                        self.rect.left = barricade.rect.right
                        self.speed_x *= -1
                        self.hit()

                else:
                    if self.speed_y > 0:  # Going down
                        self.rect.bottom = barricade.rect.top
                        self.speed_y *= -1
                        self.hit()
                    elif self.speed_y < 0:  # Going up
                        self.rect.top = barricade.rect.bottom
                        self.speed_y *= -1
                        self.hit()


class Barricade2P(pygame.sprite.Sprite):

    def __init__(self, x_size, y_size):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((x_size, y_size))
        self.rect = self.image.get_rect()
        self.x = (random.randrange(0, WIDTH))
        self.y = (random.randrange(HEIGHT / 3, HEIGHT * 2 / 3))
        self.rect.center = (self.x, self.y)
        self.team = "neutral"


class GameTwoPlayer(Game):
    """
     ____________________________________________________________________________________________________________________
     BATTLE LOOP: TWO PLAYER DUEL
     ____________________________________________________________________________________________________________________
     """

    bullets = pygame.sprite.Group()
    p1bullets = pygame.sprite.Group()
    p2bullets = pygame.sprite.Group()
    p1 = pygame.sprite.Group()
    p2 = pygame.sprite.Group()
    splatters = pygame.sprite.Group()

    DUEL_OVER = False

    if GAMEMODE == GAMEMODES[2]:
        # Sprite instances and sorting
        player1 = Player2P(RED, 100, 300, "RED")
        player2 = Player2P(BLUE, 700, 300, "BLUE")  # create instance of Player class

        p1.add(player1)
        p2.add(player2)
        ALL_SPRITES.add(player1)
        ALL_SPRITES.add(player2)
        ALL_SPRITES.add(player1.aim)
        ALL_SPRITES.add(player2.aim)

    def check_for_winner_2_p(self):
        if self.player1.hp == 0 and self.player2.hp == 0:
            say_centered("'Twas a tie.", 100, WHITE)
            say("Press enter to restart", int(HEIGHT // 16), WHITE, WIDTH / 2, HEIGHT * 3 / 4)
            self.DUEL_OVER = True
        elif self.player1.hp == 0:
            print("Player 2 (BLUE) Won")
            self.GAME_ON = False
        elif self.player2.hp == 0:
            print("Player 1 (RED) Won")
            self.GAME_ON = False

    def hit_detection_2_p(self):
        """
        group collide creates a dictionary w/ key being a sprite from 1st group and value being a list of all sprites
        from 2nd group key sprite collided w/
        """

        p1_hit_detects = collision_group(self.p1, self.p2bullets, False, True)
        # detects if enemy shot by friendly bit
        if p1_hit_detects:  # checks if hit_detects is empty
            splat = Splatter(self.player1.rect.center)
            self.splatters.add(splat)
            self.player1.hp -= 1
        p2_hit_detects = collision_group(self.p2, self.p1bullets, False, True)
        if p2_hit_detects:
            splat = Splatter(self.player2.rect.center)
            self.splatters.add(splat)
            self.player2.hp -= 1

        self.check_for_winner_2_p()

    def spawn_barricades_2_p(self, num):
        global BARRICADE_SIZE
        for i in range(1, num + 1):
            b = Barricade2P(BARRICADE_THICKNESS, BARRICADE_SIZE)
            self.ALL_SPRITES.add(b)
            self.BARRICADES.add(b)

    def battle_phase_2_player_duel(self):
        pygame.mixer.music.play(loops=-1)
        self.spawn_barricades_2_p(5)
        while game.GAME_ON:
            clock.tick(FPS)
            self.player1.fire(clock.get_time())
            self.player2.fire(clock.get_time())

            # self.ALL_SPRITES.update()  # maps the update() function over ALL_SPRITES list
            self.player1.update(pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_t, pygame.K_y)
            self.player2.update(pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RSHIFT,
                                pygame.K_RETURN)
            self.bullets.update()
            self.p1bullets.update()
            self.p2bullets.update()
            self.splatters.update()
            self.hit_detection_2_p()

            screen.fill(GRAY)

            self.ALL_SPRITES.draw(screen)

            for event in pygame.event.get():
                self.quit_loop(event)
                if self.DUEL_OVER:
                    self.check_respawn_2_p(event)
            pygame.display.flip()

    """
    ____________________________________________________________________________________________________________________
    WIN LOOP TWO PLAYER
    ____________________________________________________________________________________________________________________
    """

    def win_2_p(self, player):
        self.go_speed = GO_SPEED
        self.go_wait = GO_WAIT

        if player == "RED":
            color = RED
        else:
            color = BLUE

        while self.GAME_OVER_ON:
            clock.tick(MENU_FPS)  # limit how fast the loop runs
            if self.GO_COUNT < GO_AMOUNT:
                if self.wt_go.wait_over(self.go_wait):
                    self.spawn_gofb(color)

            for event in pygame.event.get():
                self.quit_loop(event)
                self.check_respawn_2_p(event)

            # update
            self.GAME_OVER_SPRITES.update()

            # draw
            say_centered("PLAYER ONE ({}) WON.".format(player), 100, WHITE)
            say("Press enter to restart", int(HEIGHT // 16), WHITE, WIDTH / 2, HEIGHT * 3 / 4)
            self.GAME_OVER_SPRITES.draw(screen)
            pygame.display.flip()  # "Flips blackboard," updates display MUST DO AFTER ALL COMPUTATIONS (LAST)

    def check_respawn_2_p(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.player1.hp = 5
                self.player2.hp = 5
                self.player1.rect.center = (100, 300)
                self.player2.rect.center = (700, 300)
