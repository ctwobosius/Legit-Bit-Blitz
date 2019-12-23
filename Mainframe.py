from Setup import *  # imports everything from Variables.py without having to use dot notation


"""
________________________________________________________________________________________________________________________
Game Classes: Units
________________________________________________________________________________________________________________________
"""


class SpawnPoint(pygame.sprite.Sprite):
    """Used to spawn the boss"""
    def __init__(self, player):     # creates a function for what the class should do/what traits it has at startup
        pygame.sprite.Sprite.__init__(self)                     # needed to initialize the sprite
        self.image = pygame.Surface((UNIT_SIZE, UNIT_SIZE))     # create rectangle to be drawn
        self.image.fill(PURPLE)            # fill the image with purple
        self.rect = self.image.get_rect()  # set hitbox, rect stores the coordinates
        self.rect.center = player.rect.center
        self.rect.centery -= 1100          # set the spawnpoint to be 1100 pixels above the player
        pygame.draw.rect(self.image, WHITE, self.image.get_rect(), 2)    # hitboxes, also a graphical effect


class Unit(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((UNIT_SIZE, UNIT_SIZE))
        self.rect = self.image.get_rect()       # set hitbox, rect stores the coordinates
        self.speed_x = random_direction() * random.randrange(75, 125) / 100 * UNIT_SPEED
        self.speed_y = random_direction() * random.randrange(75, 125) / 100 * UNIT_SPEED
        self.fire_delay = random.randrange(-UNIT_FIRE_DELAY, UNIT_FIRE_DELAY + 1)
        # randomized so they all don't fire at once
        self.team = "neutral"
        self.hp = 1
        self.type = "Grunt"
        self.first_shot = False
        self.fire_interval = UNIT_FIRE_DELAY
        self.boss = False

    def change_size(self, size):
        """changes the unit's size"""
        old_cent = self.rect.center     # needed because self.rect.center is deleted when self.image is reset
        self.image = pygame.Surface((size, size))
        self.rect = self.image.get_rect()
        self.rect.center = old_cent

    def move_one_direction(self, speed_x, speed_y):
        """Used in move to treat each axis as a separate thing to be updated;
        You need to move one direction at a time so that when colliding with barricades, it won't create a bug where
        inputting both an x and y direction will teleport the player to the corner; for example, moving right and moving
        up, the player's x position and y position will be changed, and the player will be teleported to the bottom left
        hand corner, because both conditions are activated. However, we want the player to keep the same x position if
        he is moving up, and the same y position if he is moving down, which can't be achieved without one direction
        because operating on both positions will change both x and y. It's sort of like livelock.

        This collision method was made possible by https://www.pygame.org/project-Rect+Collision+Response-1061-.html"""
        self.rect.x += speed_x
        self.bounce("x")
        self.rect.y += speed_y
        self.bounce("y")

    def move(self, speed_x, speed_y):
        """Moves the unit in both directions"""
        if speed_x != 0:
            self.move_one_direction(speed_x, 0)
        if speed_y != 0:
            self.move_one_direction(0, speed_y)

    def reset_direction(self, direction):
        """Sets speed in one axis to a slower or faster speed"""
        if direction == "x":
            if abs(self.speed_x) < UNIT_SPEED * 2:
                self.speed_x *= random.randrange(75, 125) / 100
            else:
                self.speed_y *= random.randrange(80, 100) / 100
        else:
            if abs(self.speed_y) < UNIT_SPEED * 2:
                self.speed_y *= random.randrange(75, 125) / 100
            else:
                self.speed_y *= random.randrange(80, 100) / 100

    def bounce(self, direction):
        """Makes the unit bounce if it hits a barricade"""
        for barricade in game.BARRICADES:          # game is the instance of the Game class which is further down
            if self.rect.colliderect(barricade.rect):  # if the list of collisions are not empty
                if direction == "x":
                    if self.speed_x > 0:  # Going right
                        self.rect.right = barricade.rect.left
                        self.reset_direction(direction)
                        self.speed_x *= -1

                    elif self.speed_x < 0:  # Going left
                        self.rect.left = barricade.rect.right
                        self.reset_direction(direction)
                        self.speed_x *= -1
                else:
                    if self.speed_y > 0:  # Going down
                        self.rect.bottom = barricade.rect.top
                        self.reset_direction(direction)
                        self.speed_y *= -1

                    elif self.speed_y < 0:  # Going up
                        self.rect.top = barricade.rect.bottom
                        self.reset_direction(direction)
                        self.speed_y *= -1

    def update(self):
        """All sprites with update are updating using the sprite.update() command"""
        self.move(self.speed_x, self.speed_y)

    def calc_shoot_vect_ang(self):
        """Calculates the x speed, y speed, and angle needed to shoot at someone at the opposing side.
        Creates a list of all sprites on the opposing side that have not done self.kill(), then chooses one at random
        to do the calculations.  Boy, I love vectors with the pygame coordinate system.

        p_x and p_y are the positions of the object the unit is shooting at,
        self_x and self_y are the unit's coordinates"""
        self_x = self.rect.centerx
        self_y = self.rect.centery
        targets = []
        if self.team == TEAMS[0]:
            for friendly in game.FRIENDLIES:
                targets.append(friendly)
            targets.append(game.player)
            try:
                target = random.choice(targets)
            except IndexError:
                target = game.player
            p_x = target.rect.centerx
            p_y = target.rect.centery
        else:
            for enemy in game.ENEMIES:
                targets.append(enemy)

            try:
                targets.append(game.boss)
            except AttributeError:
                pass

            try:
                target = random.choice(targets)
            except IndexError:
                target = game.player
            p_x = target.rect.centerx
            p_y = target.rect.centery

        theta = math.atan2((p_y - self_y), (p_x - self_x))
        # use atan2 because it corrects for when p_x - self_x = 0 (division by zero normally)

        bit_x_dir = math.cos(theta)
        bit_y_dir = math.sin(theta)

        return((bit_x_dir, bit_y_dir, theta))

    def which_side(self, x_direction, y_direction):
        """this block sets what side of the unit the bit spawns on (the "direction")"""
        if abs(x_direction) > abs(y_direction):
            if x_direction < 0:  # shooting left
                return (self.rect.left, self.rect.centery)
            elif x_direction > 0:  # shooting right
                return (self.rect.right, self.rect.centery)
        else:
            if y_direction < 0:  # shooting up
                return (self.rect.centerx, self.rect.top)
            else:  # shooting down
                return (self.rect.centerx, self.rect.bottom)

    def shoot_single(self):
        """The function that actually spawns a bit"""
        bit_dir = self.calc_shoot_vect_ang()
        bit_x_dir = bit_dir[0]
        bit_y_dir = bit_dir[1]
        angle = bit_dir[2]
        side_pos = self.which_side(bit_x_dir, bit_y_dir)
        bit = Bit(side_pos[0], side_pos[1], BIT_SPEED, bit_x_dir, bit_y_dir, self.team, angle)
        if self.team == TEAMS[0]:
            game.BITS_HOSTILE.add(bit)
        else:
            game.BITS_FRIENDLY.add(bit)
        game.BITS.add(bit)
        game.ALL_SPRITES.add(bit)
        game.BATTLE_SPRITES.add(bit)
        game.BITS_NONPIERCING.add(bit)

    def shoot_shotgun(self):
        """Spawns a spread of bits"""
        bit_dir = self.calc_shoot_vect_ang()
        bit_x_dir = bit_dir[0]
        bit_y_dir = bit_dir[1]
        angle = bit_dir[2]
        side_pos = self.which_side(bit_x_dir, bit_y_dir)
        s = SHOTGUN_SPREAD * 1000
        if self.boss:
            SHOTGUN_BOSS_SOUND.play()
        for shot in range(SHOTGUN_AMOUNT):
            spread_x = random.randrange(-s, s + 1) / 1000
            spread_y = random.randrange(-s, s + 1) / 1000
            bit = Bit(side_pos[0], side_pos[1], BIT_SPEED, bit_x_dir + spread_x, bit_y_dir + spread_y, self.team,
                      angle)
            game.BITS.add(bit)
            if self.team == TEAMS[0]:
                game.BITS_HOSTILE.add(bit)
            else:
                game.BITS_FRIENDLY.add(bit)
            game.ALL_SPRITES.add(bit)
            game.BATTLE_SPRITES.add(bit)
            game.BITS_NONPIERCING.add(bit)

    def shoot_first_shot(self):
        """Needed so that units don't all fire at once"""
        if self.type == LIST_OF_CLASSES[0] or self.type == LIST_OF_CLASSES[3]:
            if self.fire_delay >= UNIT_FIRE_DELAY:
                self.shoot_single()
                self.fire_delay = pygame.time.get_ticks()  # sets fire delay to the last time a shot was fired
                self.first_shot = True
        elif self.type == LIST_OF_CLASSES[1]:
            if self.fire_delay >= UNIT_FIRE_DELAY:
                self.shoot_shotgun()
                self.fire_delay = pygame.time.get_ticks()
                self.first_shot = True
        elif self.type == LIST_OF_CLASSES[2]:
            if self.fire_delay >= UNIT_FIRE_DELAY / 10:
                self.shoot_single()
                self.fire_delay = pygame.time.get_ticks()
                self.first_shot = True
        self.fire_delay += clock.get_time()

    def fire(self):
        """Does the shoot function (which spawns a bit or bits) if a certain time has elapsed"""
        if not self.first_shot:
            self.shoot_first_shot()
        else:
            time = pygame.time.get_ticks()  # gets time in ms since pygame.clock started
            if self.type == LIST_OF_CLASSES[0] or self.type == LIST_OF_CLASSES[3]:
                if time - self.fire_delay > self.fire_interval:
                    self.shoot_single()
                    self.fire_delay = pygame.time.get_ticks()  # sets fire delay to the last time a shot was fired

            elif self.type == LIST_OF_CLASSES[1]:
                if time - self.fire_delay > self.fire_interval:
                    self.shoot_shotgun()
                    self.fire_delay = pygame.time.get_ticks()

            elif self.type == LIST_OF_CLASSES[2]:
                if time - self.fire_delay > self.fire_interval:
                    self.shoot_single()
                    self.fire_delay = pygame.time.get_ticks()

        # helped by https://www.reddit.com/r/pygame/comments/5r75q1/how_to_get_each_sprite_to_fire_a_bullet/


class Enemy(Unit):
    def __init__(self):
        super().__init__()
        self.image.fill(RED)
        self.x = (random.randrange(self.rect.width, WIDTH - self.rect.width))       # Our spawning algorithm
        self.y = (random.randrange(HEIGHT / 3 - int(WALL_SIZE / 3), self.rect.height))
        self.rect.center = (self.x, self.y)
        self.team = TEAMS[0]

    def change_size(self, size):
        """super is used to add on to the parent's "change_size", in this case adding code that fills the enemy with
        the color red"""
        super(Enemy, self).change_size(size)
        self.image.fill(RED)


class Boss(Enemy):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        super().__init__()
        self.speed_x = random_direction() * random.randrange(150, 200) / 100 * UNIT_SPEED
        self.speed_y = random_direction() * random.randrange(150, 200) / 100 * UNIT_SPEED
        self.rect.center = center
        self.hp = 30 + int(FRIENDLY_AMOUNT) - int(ENEMY_AMOUNT)
        self.fire_delay = -500
        self.last_time_type = 7000
        self.boss = True
        self.change_size(UNIT_SIZE * 2)
        self.hold_fire = True

    def reset_direction(self, direction):
        """Redefined to make boss faster"""
        if direction == "x":
            if abs(self.speed_x) < UNIT_SPEED * 2.5:
                self.speed_x *= random.randrange(90, 115) / 100
            else:
                self.speed_y *= random.randrange(80, 100) / 100
        else:
            if abs(self.speed_y) < UNIT_SPEED * 2.5:
                self.speed_y *= random.randrange(90, 115) / 100
            else:
                self.speed_y *= random.randrange(80, 100) / 100

    def change_type(self):
        """If called, randomly changes the boss's type to either machinegun fire or shotgun fire"""
        time_since_last_call = clock.get_time()
        self.last_time_type += time_since_last_call
        if self.last_time_type >= 10000:    # doesn't allow change unless 10 secs have passed since it last changed
            self.hold_fire = True
            self.last_time_type = 0
            self.type = pick_one(LIST_OF_CLASSES[1], LIST_OF_CLASSES[2])

            if self.type == LIST_OF_CLASSES[1]:     # necessary to get the audio synced with gunfire
                self.fire_interval = UNIT_FIRE_DELAY / 2
            else:
                self.fire_interval = UNIT_FIRE_DELAY / 15
                MINIGUN_SOUND.play()

    def fire(self):
        """Does the shoot function (which spawns a bit) if a certain time has elapsed"""
        if not self.first_shot:
            self.shoot_first_shot()
        else:
            time = pygame.time.get_ticks()  # gets time in ms since pygame.clock started
            if self.type == LIST_OF_CLASSES[0] or self.type == LIST_OF_CLASSES[3]:
                if time - self.fire_delay > self.fire_interval:
                    self.shoot_single()
                    self.fire_delay = pygame.time.get_ticks()  # sets fire delay to the last time a shot was fired

            elif self.type == LIST_OF_CLASSES[1]:
                if time - self.fire_delay > self.fire_interval:
                    self.shoot_shotgun()
                    self.fire_delay = pygame.time.get_ticks()

            elif self.type == LIST_OF_CLASSES[2]:
                if self.hold_fire:
                    if time - self.fire_delay > 1000:
                        self.hold_fire = False
                if not self.hold_fire:
                    if time - self.fire_delay > self.fire_interval:
                        self.shoot_single()
                        self.fire_delay = pygame.time.get_ticks()

    # def charge(self):
    #     """This function would've had the boss charge at a random friendly or the player"""
    #     direction = self.calc_shoot_vect_ang()
    #     self.speed_x = direction[1] * UNIT_SPEED * 2
    #     self.speed_y = direction[2] * UNIT_SPEED * 2


class Friendly(Unit):

    def __init__(self):
        super().__init__()
        self.image.fill(BLUE)    # fill rectangle
        self.x = (random.randrange(LEFT + UNIT_SIZE, RIGHT - UNIT_SIZE))        # Our spawning algorithm
        self.y = (random.randrange(WALL_SIZE / 3, WALL_SIZE / 2 - self.rect.height))
        self.rect.center = (self.x, self.y)
        self.team = TEAMS[1]

    def change_size(self, size):
        """Changes the size of the unit and fills the enemy with the color blue"""
        super(Friendly, self).change_size(size)
        self.image.fill(BLUE)


class Player(Unit):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # graphics
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        # self.image = pygame.image.load(os.path.join(graphics_directory, "Alonzo.png")).convert()
            # convert into form pygame can manipulate, Alonzo.png is 20 x 20 pxls
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width / 2)
        # pygame.draw.circle(self.image, BLUE, self.rect.center, self.radius)
        self.rect.center = (WIDTH / 2, 3 * HEIGHT / 4)                  # sets position of rectangle
        self.speed_x = 0                # creates variable "speedx" for each instance of self (player)
        self.speed_y = 0
        self.hp = PLAYER_HP
        self.fire_delay = 0
        self.shield_counter = 0
        self.weapon = 2
        self.shotgun_unlocked = True
        self.team = TEAMS[1]
        self.boss = False

    def key_pressed(self):
        """Moves if keys are pressed, and "moves the camera" if player moves too far off center"""
        key_state = pygame.key.get_pressed()
        speed = PLAYER_SPEED            # speed and camera_speed needed for sprint to work correctly
        camera_speed = PLAYER_SPEED
        if key_state[pygame.K_LSHIFT]:  # sprint with shift
            speed *= 2
            camera_speed = speed
        if key_state[pygame.K_w]:       # standard WASD movement
            self.move(0, -speed)

        if key_state[pygame.K_a]:
            self.move(-speed, 0)

        if key_state[pygame.K_s]:
            self.move(0, speed)

        if key_state[pygame.K_d]:
            self.move(speed, 0)

        # switch weapons
        if key_state[pygame.K_1]:
            self.del_shield()
            self.shield_counter = 0
            self.weapon = 1
            self.spawn_p_shield()
        elif key_state[pygame.K_2]:
            self.weapon = 2
            self.del_shield()
        elif key_state[pygame.K_3]:
            self.weapon = 3
            self.del_shield()
        # elif key_state[pygame.K_4]:
        #     self.weapon = 4
        #     self.del_shield()

        # camera algorithm
        if self.rect.left > WIDTH * 6 / 10:     # if reach certain spot
            for item in game.BATTLE_SPRITES:
                item.rect.x -= camera_speed     # moves items to mimic camera movement
        if self.rect.right < WIDTH * 4 / 10:
            for item in game.BATTLE_SPRITES:
                item.rect.x += camera_speed
        if self.rect.top > HEIGHT * 6 / 10:
            for item in game.BATTLE_SPRITES:
                item.rect.y -= camera_speed
        if self.rect.bottom < HEIGHT * 4 / 10:
            for item in game.BATTLE_SPRITES:
                item.rect.y += camera_speed

        return camera_speed

    def switch_weap(self):
        """Cycles through weapons"""
        self.weapon += 1
        if self.weapon != 1:
            self.del_shield()
        if self.weapon > 3:
            self.weapon = 1
            self.spawn_p_shield()

    def spawn_p_shield(self):
        """spawns a shield for the player"""
        if self.weapon == 1 and self.shield_counter == 0:
            global PLAYER_SHIELD
            PLAYER_SHIELD = PlayerShield(self)
            game.ALL_SPRITES.add(PLAYER_SHIELD)  # adds player instance to list
            game.BATTLE_SPRITES.add(PLAYER_SHIELD)
            game.BARRICADES_FRIENDLY.add(PLAYER_SHIELD)
            self.shield_counter = 1

    def update(self):
        self.speed_x = 0        # reset speed every frame
        self.speed_y = 0
        camera_speed = self.key_pressed()
        mouse_state = pygame.mouse.get_pressed()[0]     # returns True if left mouse button is clicked
        if mouse_state:
            self.auto_fire()

        # camera moves if mouse is at edge
        m_pos = pygame.mouse.get_pos()
        mouse_x = m_pos[0]
        mouse_y = m_pos[1]
        if mouse_x >= WIDTH:  # if mouse reach edge
            for item in game.BATTLE_SPRITES:
                item.rect.x -= camera_speed     # moves items to mimic camera movement
        if mouse_x <= 0:
            for item in game.BATTLE_SPRITES:
                item.rect.x += camera_speed
        if mouse_y >= HEIGHT - 1:
            for item in game.BATTLE_SPRITES:
                item.rect.y -= camera_speed
        if mouse_y <= 0:
            for item in game.BATTLE_SPRITES:
                item.rect.y += camera_speed

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
        self.rect.x += speed_x      # moves sprite's x coordinates by speed_x
        self.rect.y += speed_y
        self.stop()

    def stop(self):
        """If the player collides with a barricade, stop the player's movement"""
        for barricade in game.BARRICADES:
            if self.rect.colliderect(barricade.rect):       # detects collision with right side of barricade
                if self.speed_x > 0:    # Going right
                    self.rect.right = barricade.rect.left
                if self.speed_x < 0:    # Going left
                    self.rect.left = barricade.rect.right
                if self.speed_y > 0:     # Going down
                    self.rect.bottom = barricade.rect.top
                if self.speed_y < 0:     # Going up
                    self.rect.top = barricade.rect.bottom

    def calc_shoot_vect_ang(self):
        """This version is used to calculate the vectors and angle necessary to shoot a bit at the mouse."""
        m_pos = pygame.mouse.get_pos()
        mouse_x = m_pos[0]
        mouse_y = m_pos[1]
        p_x = self.rect.centerx
        p_y = self.rect.centery
        theta = math.atan2((mouse_y - p_y), (mouse_x - p_x))

        bit_x_dir = math.cos(theta)
        bit_y_dir = math.sin(theta)

        return ((bit_x_dir, bit_y_dir, theta))

    def auto_fire(self):
        """Used to create a time delay between shots"""
        current_time = pygame.time.get_ticks()
        if self.weapon == 2:
            if current_time - self.fire_delay > PLAYER_FIRE_DELAY:
                self.shoot_single()
                SHOOT_SOUND.play()
                self.fire_delay = pygame.time.get_ticks()

        elif self.weapon == 3 and self.shotgun_unlocked:
            if current_time - self.fire_delay > PLAYER_SHOTGUN_DELAY:
                self.shoot_shotgun()
                self.fire_delay = pygame.time.get_ticks()
                SHOTGUN_SOUND.play()

    def del_shield(self):
        """Removes the player's shield"""
        self.shield_counter = 0
        try:
            PLAYER_SHIELD.kill()
        except NameError:
            pass


"""
________________________________________________________________________________________________________________________
Other Game Classes
________________________________________________________________________________________________________________________
"""


class Bit(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, x_direction, y_direction, team, theta):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = pygame.Surface((BIT_SIZE, BIT_THICKNESS)).convert_alpha()
        # convert_alpha needed to rotate the image
        if team == TEAMS[0]:
            self.image_orig.fill(RED)
        elif team == TEAMS[1]:
            self.image_orig.fill(BLUE)
        else:
            self.image_orig.fill(BLACK)

        self.image = pygame.transform.rotate(self.image_orig, math.degrees(-theta) % 360)
        # remainder 360 stops unnecessary calculations since one full rotation is only 360 degrees, and we use the
        # original image because rotating an already rotated image will distort it more than necessary
        self.rect = self.image_orig.get_rect()
        self.rect.center = (x, y)

        self.speed_y = y_direction * speed
        self.speed_x = x_direction * speed
        self.hp = 1

    def hit(self):
        """Stops bit from running continuously """
        self.hp -= 1
        if self.hp <= 0:
            self.kill()

    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        # pygame.draw.rect(self.image, YELLOW, self.image.get_rect(), 1)


class Wall(pygame.sprite.Sprite):
    team = "neutral"            # all Walls spawn as neutral unless otherwise changed

    def __init__(self, x_size, y_size, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((x_size, y_size))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)          # set its topleft coordinate to be x, y


class Barricade(Wall):
    def __init__(self, x_size, y_size, x, y):
        super(Barricade, self).__init__(x_size, y_size, x, y)
        # original spawning algorithm, the newer one is in the Game class
            # x = (random.randrange(LEFT + BARRICADE_SIZE, RIGHT - BARRICADE_SIZE))
            # y = (random.randrange(int(TOP / 1.3), int(BOTTOM / 1.3)))
        self.rect.topleft = (x, y)       # set spawnpoint


class PlayerShield(Player):
    def __init__(self, player):
        pygame.sprite.Sprite.__init__(self)
        self.team = "neutral"
        self.image_orig = pygame.Surface((SHIELD_THICKNESS, SHIELD_SIZE)).convert_alpha()
        self.image = self.image_orig
        self.rect = self.image.get_rect()
        self.rect.centerx = player.rect.right
        self.rect.centery = player.rect.centery

    def update(self):
        """Rotates the shield to be perpendicular to the line between the mouse and the player"""
        theta = self.calc_shoot_vect_ang()[2]
        x_offset = math.cos(theta) * PLAYER_SIZE * 1.1
        y_offset = math.sin(theta) * PLAYER_SIZE * 1.1
        self.image = pygame.transform.rotate(self.image_orig, math.degrees(-theta) % 360)
        self.rect = self.image.get_rect()
        x = game.player.rect.centerx + x_offset
        y = game.player.rect.centery + y_offset
        self.rect.center = (x, y)
        # pygame.draw.rect(self.image, YELLOW, self.image.get_rect(), 1)

        self.speed_x = 0        # reset speed every frame
        self.speed_y = 0
        self.key_pressed()

    def move_one_direction(self, speed_x, speed_y):
        """Redefined so it doesn't collide with other barriers"""
        self.rect.x += speed_x
        self.rect.y += speed_y

    def key_pressed(self):
        """Used so that the shield follows the player when the player moves"""
        key_state = pygame.key.get_pressed()
        speed = PLAYER_SPEED
        if key_state[pygame.K_LSHIFT]:  # sprint with shift
            speed *= 2
        if key_state[pygame.K_w]:  # standard WASD movement
            self.move(0, -speed)
        if key_state[pygame.K_a]:
            self.move(-speed, 0)
        if key_state[pygame.K_s]:
            self.move(0, speed)
        if key_state[pygame.K_d]:
            self.move(speed, 0)


class Splatter(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.image = SPLATTER_LIST[0]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_time = 0
        self.has_player = False
        self.total_frames = len(SPLATTER_LIST)
        self.frame_rate = 100
        game.ALL_SPRITES.add(self)
        game.BATTLE_SPRITES.add(self)
        random.choice(PAIN_SOUNDS).play()

    def create_screenshake(self):
        """Enables the splatter to create a screenshake effect"""
        self.has_player = True

    def extend(self):
        """Extends the length of the screenshake effect"""
        self.total_frames += 4 + len(SPLATTER_LIST)     # 9 frames
        self.frame_rate -= 25

    def update(self):
        """Animates the splatter using time and the instance's frame variable"""
        time_since_last_call = clock.get_time()
        self.last_time += time_since_last_call
        if self.last_time >= self.frame_rate:
            self.last_time = 0
            self.frame += 1
            if self.frame >= self.total_frames:
                self.kill()
            else:
                if self.has_player:
                    self.screenshake()
                old_cen = self.rect.center
                # does nothing in the case that the extend function extends it beyond the Splatter's full animation
                try:
                    self.image = SPLATTER_LIST[self.frame]
                    self.image.set_colorkey(BLACK)
                    self.rect = self.image.get_rect()
                    self.rect.center = old_cen
                except IndexError:
                    pass

    def screenshake(self):
        global SCREENSHAKE_SIZE
        if self.frame % 2 != 0:
            for item in game.BATTLE_SPRITES:
                item.rect.y += SCREENSHAKE_SIZE
        else:
            for item in game.BATTLE_SPRITES:
                item.rect.y -= SCREENSHAKE_SIZE








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
        # hitboxes
        self.rect = self.image.get_rect()  # sets hitbox
        self.radius = int(self.rect.width / 3)
        self.rect.center = (x, y)  # sets position of rectangle
        self.speed_x = 0  # creates variable "speedx" for each instance of self (player)
        self.speed_y = 0
        self.fire_delay = 0
        self.r = 70
        self.theta = PI / 2

        self.team = team
        self.hp = 5

        self.aimx = self.rect.centerx + (self.r * math.cos(self.theta))
        self.aimy = self.rect.centery + (self.r * math.sin(self.theta))
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

        bit_x_dir = BIT_SPEED * math.sin(theta2)
        bit_y_dir = BIT_SPEED * math.cos(theta2)

        bit = Bit2P(self.rect.centerx, self.rect.centery, 1, bit_y_dir, bit_x_dir, self.team, theta2)
        game.ALL_SPRITES.add(bit)
        game.bullets.add(bit)

        if self.team == TEAMS[0]:
            game.p1bullets.add(bit)
        if self.team == TEAMS[1]:
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
        self.image = pygame.Surface((AIM_SIZE, AIM_SIZE))
        self.image.fill(color)  # fill rectangle
        self.rect = self.image.get_rect()  # set hitbox
        self.rect.center = (x, y)

    def update(self, x, y):
        self.rect.center = (x, y)


class Bit2P(Bit):
    def __init__(self, x, y, speed, y_direction, x_direction, team, theta):
        super(Bit2P, self).__init__(x, y, speed, y_direction, x_direction, team, theta)
        self.theta = theta
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
            self.rect.top = HEIGHT
        if self.rect.top > HEIGHT:
            self.hit()
            self.rect.bottom = 0
        if self.rect.left > WIDTH:
            self.hit()
            self.rect.right = 0
        if self.rect.right < 0:
            self.hit()
            self.rect.left = WIDTH

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
                old_cent = self.rect.center
                if self.theta >= 0:     # if theta is positive (using pygame coords, that means it's between quadrants III and IV)
                    self.image = pygame.transform.rotate(self.image_orig, math.degrees((self.theta) % 360) + 180)
                elif -180 >= math.degrees(self.theta) >= -135:
                    self.image = pygame.transform.rotate(self.image_orig, -math.degrees((self.theta) % 360) - 180)
                elif -135 >= math.degrees(self.theta) >= -90:
                    self.image = pygame.transform.rotate(self.image_orig, -math.degrees((self.theta) % 360) + 270)
                elif -90 >= math.degrees(self.theta) >= -45:
                    self.image = pygame.transform.rotate(self.image_orig, -math.degrees((self.theta) % 360) + 180)
                elif -45 >= math.degrees(self.theta) >= 0:
                    self.image = pygame.transform.rotate(self.image_orig, -math.degrees((self.theta) % 360) - 90)
                self.rect = self.image_orig.get_rect()
                self.rect.center = old_cent

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
        self.x = (random.randrange(WIDTH / 3, WIDTH * 2 / 3))
        self.y = (random.randrange(HEIGHT / 3, HEIGHT * 2 / 3))
        self.rect.center = (self.x, self.y)
        self.team = "neutral"











"""
________________________________________________________________________________________________________________________
MAIN GAME CLASS
________________________________________________________________________________________________________________________
"""


class GAME():
    """The grand, the vast, the overwhelming...Gaaammmeee claaaassss!!! Creating a class for the game allows us to
    repeat functions pretty easily, allowing us to transition between the menu, the game, game over screens, etc,
    as well as to create game state variables that don't need to be global variables"""
    """
    ____________________________________________________________________________________________________________________
    Game State Variables
    ____________________________________________________________________________________________________________________
    """
    GAME_ON = True

    # Menu Variables
    INTRO_ON = True
    MENU_ON = True
    BATTLE_PHASE = False
    wt_fb = WaitTimer()
    # intro vars
    FB_COUNT = 1
    fb_wait = FB_WAIT

    # Battle Phase variables
    PREPPING = True
    PLAYER_ALIVE = True
    ENEMY_COUNT = 0
    FRIENDLY_COUNT = 0

    # Win variables
    WIN_ON = False
    FINAL_STAGE = False
    BOSS_DEAD = False

    # Game over variables
    GAME_OVER_ON = False
    GO_COUNT = 0
    go_speed = GO_SPEED
    go_wait = GO_WAIT
    wt_go = WaitTimer()

    """
    ____________________________________________________________________________________________________________________
    Sprite Groups
    ____________________________________________________________________________________________________________________
    """
    MENU_SPRITES = pygame.sprite.Group()  # creates a group named "menu_sprites"
    ALL_SPRITES = pygame.sprite.Group()  # creates a list named "ALL_SPRITES"
    BATTLE_SPRITES = pygame.sprite.Group()
    UNITS = pygame.sprite.Group()
    ENEMIES = pygame.sprite.Group()
    FRIENDLIES = pygame.sprite.Group()
    BITS = pygame.sprite.Group()
    BITS_NONPIERCING = pygame.sprite.Group()
    BITS_FRIENDLY = pygame.sprite.Group()
    BITS_HOSTILE = pygame.sprite.Group()
    BARRICADES = pygame.sprite.Group()
    BARRICADES_NEUTRAL = pygame.sprite.Group()
    BARRICADES_FRIENDLY = pygame.sprite.Group()
    BARRICADES_ENEMY = pygame.sprite.Group()
    WIN_SPRITES = pygame.sprite.Group()
    GAME_OVER_SPRITES = pygame.sprite.Group()

    # created instance here to start manipulating the player
    if GAMEMODE != GAMEMODES[2]:
        player = Player()           # create instance of the singleplayer Player class
        ALL_SPRITES.add(player)     # adds player instance to the pygame "Group" data structure
        BATTLE_SPRITES.add(player)

    """
    ____________________________________________________________________________________________________________________
    Game Functions
    ____________________________________________________________________________________________________________________
    """

    def __init__(self):
        self.player_hit = False

    def game_quit(self):
        """quits the game, didn't directly do pygame.quit() because then it would error since the code below"""
        global QUIT
        self.INTRO_ON = False
        self.MENU_ON = False
        self.PREPPING = False
        self.GAME_ON = False
        self.WIN_ON = False
        self.GAME_OVER_ON = False
        self.PLAYER_ALIVE = False
        QUIT = True

    def press_esc(self):
        """Also quits the game, was going to use this to restart the program to change variables in the console but
        after you do pygame.quit, you can't reopen pygame, so we were going to figure this out later"""
        self.INTRO_ON = False
        self.MENU_ON = False
        self.PREPPING = False
        self.GAME_ON = False
        self.WIN_ON = False
        self.GAME_OVER_ON = False
        self.PLAYER_ALIVE = False

    def quit_loop(self, event):
        """This is used in every stage of the game (loop functions), and quits the entire game loop
         by calling the functions above"""
        if event.type == pygame.QUIT:
            self.game_quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.press_esc()

    def spawn_fb(self):
        """Spawns a falling block."""
        fb = FallingBlock(BLUE, 7.5, FB_SPEED)
        self.MENU_SPRITES.add(fb)
        self.FB_COUNT += 1
        self.fb_wait *= .8  # spawns falling blocks faster and faster

    """
    ____________________________________________________________________________________________________________________
    Intro Loop
    ____________________________________________________________________________________________________________________
    """
    def intro(self):
        while self.INTRO_ON:
            clock.tick(INTRO_FPS)
            # limits how fast the while loop runs (If FPS = 60, loop will only run if 1/60th of a second has passed)

            # Calculation section: do calculations, do functions, and execute code
            if self.FB_COUNT < FB_AMOUNT:      # limit amount of falling blocks (fb's)
                if self.wt_fb.wait_over(self.fb_wait):
                    self.spawn_fb()
            else:
                self.INTRO_ON = False     # once there are FB_AMOUNT of fb's, stop spawning blocks and turn off the loop

            for event in pygame.event.get():
                self.quit_loop(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:        # press enter to skip the intro
                        for i in range(FB_AMOUNT - self.FB_COUNT):
                            self.spawn_fb()
                        self.INTRO_ON = False

            # Update section: update the sprite group with their new values
            self.MENU_SPRITES.update()

            # Draw section: draw sprites and stuff on the screen
            screen.fill(DDGRAY)
            self.MENU_SPRITES.draw(screen)
            pygame.display.flip()  # "Flips blackboard/updates display," DO THIS LAST OR IT WON'T DRAW EVERYTHING

    """
    ____________________________________________________________________________________________________________________
    MAIN MENU LOOP
    ____________________________________________________________________________________________________________________
    """

    def main_menu(self):
        fb = FallingBlock(BLUE, 7.5, FB_SPEED)
        self.MENU_SPRITES.add(fb)
        self.FB_COUNT += 1

        while self.MENU_ON:
            clock.tick(MENU_FPS)

            # calculations
            self.intro()
            for event in pygame.event.get():
                self.quit_loop(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.MENU_ON = False
                        self.BATTLE_PHASE = True

            # update
            self.MENU_SPRITES.update()

            # draw
            screen.fill(DGRAY)
            self.MENU_SPRITES.draw(screen)
            say_centered("Legit Bit Blitz", int(HEIGHT // 8), WHITE)
            say("Press enter to start", int(HEIGHT // 16), WHITE, WIDTH / 2, HEIGHT * 3 / 4)
            pygame.display.flip()

    """
    ____________________________________________________________________________________________________________________
    Battle Functions
    ____________________________________________________________________________________________________________________
    """

    def choose_type(self, unit, prob_shotgun, prob_auto, prob_tank):
        """set the inputted unit to a random type based on the probabilities (eg: if unit = enemy and prob_shotgun = .2,
        then the enemy unit has a 20% chance of becoming a shotgunner"""
        if HARDMODE_ON:
            if return_bool_probability(prob_shotgun):
                unit.type = LIST_OF_CLASSES[1]
            elif return_bool_probability(prob_auto):
                unit.type = LIST_OF_CLASSES[2]
                unit.fire_interval = UNIT_FIRE_DELAY / 10
            elif return_bool_probability(prob_tank):
                unit.type = LIST_OF_CLASSES[3]
                unit.change_size(UNIT_SIZE + 5)
                unit.hp = 10

    def spawn_unit(self, unit_class):
        """spawn units of the "unit_class" type, and append them to the correct pygame Groups,
        and edit the unit counters"""
        unit = unit_class()
        self.ALL_SPRITES.add(unit)
        self.BATTLE_SPRITES.add(unit)
        self.UNITS.add(unit)
        if unit_class == Enemy:
            self.ENEMY_COUNT += 1
            self.ENEMIES.add(unit)
            self.choose_type(unit, .15, .15, .15)
        else:
            self.FRIENDLY_COUNT += 1
            self.FRIENDLIES.add(unit)
            self.choose_type(unit, .1, .1, .1)

    def spawn_units_recursive(self, unit_class, num):
        """Spawn "num" number of units the extra way (through recursion!), the type (eg: enemy or friendly) is
        determined by the unit_class parameter"""
        if num <= 0:
            pass
        else:
            self.spawn_unit(unit_class)
            self.spawn_units_recursive(unit_class, num - 1)

    def spawn_barricade(self, barricade_class, x, y):
        """Spawn a singular barricade at (x, y)"""
        b = barricade_class(BARRICADE_SIZE, BARRICADE_THICKNESS, x, y)
        self.ALL_SPRITES.add(b)
        self.BATTLE_SPRITES.add(b)
        self.BARRICADES.add(b)
        if barricade_class.team == "neutral":
            self.BARRICADES_NEUTRAL.add(b)

    def spawn_all_barricades(self, barricade_class, num):
        """Uses list comprehensions to create a "grid" of coordinates where the barricades are spawned at"""
        b_counter = 0
        x_coords = [x for x in range(int(PLAY_AREA_LEFT), int(PLAY_AREA_RIGHT) - BARRICADE_SIZE + 1) if x % 20 == 0]
        y_coords = [y for y in range(int(PLAY_AREA_TOP) + BARRICADE_SIZE, int(PLAY_AREA_BOTTOM) - BARRICADE_SIZE + 1) if y % 133 == 0]
        for i in range(num):
            if b_counter < num:
                x = random.choice(x_coords)
                y = random.choice(y_coords)
                self.spawn_barricade(barricade_class, x, y)
                b_counter += 1

    def spawn_wall(self, x, y, orientation):
        """Spawns a "large barricade" that serves as the boundaries that units can't move past"""
        if orientation == "vertical":
            b = Wall(WALL_THICKNESS, WALL_SIZE, x, y)
        else:
            b = Wall(WALL_SIZE, WALL_THICKNESS, x, y)
        self.ALL_SPRITES.add(b)
        self.BARRICADES_NEUTRAL.add(b)
        self.BATTLE_SPRITES.add(b)
        self.BARRICADES.add(b)

    def spawn_border(self):
        """Spawns a box of walls"""
        self.spawn_wall(LEFT, TOP, "vertical")     # left wall
        self.spawn_wall(LEFT, TOP, "horizontal")       # top wall
        self.spawn_wall(RIGHT, TOP, "vertical")         # right wall
        self.spawn_wall(LEFT, BOTTOM - WALL_THICKNESS, "horizontal")   # bottom wall

    def check_win(self):
        """Checks if the list of enemies is empty, and if hardmode is on, it'll spawn the boss and check if the boss
        is dead"""
        if not self.ENEMIES:
            if not HARDMODE_ON:
                self.PLAYER_ALIVE = False
                self.WIN_ON = True
            elif HARDMODE_ON and not self.FINAL_STAGE:
                self.spawn_boss()
                self.FINAL_STAGE = True
            elif HARDMODE_ON and self.BOSS_DEAD:
                self.PLAYER_ALIVE = False
                self.WIN_ON = True

    def check_lose(self):
        """checks if player has lost all their hp"""
        if self.player.hp <= 0:
            self.PLAYER_ALIVE = False  # if player has hit any enemy, game over
            self.GAME_OVER_ON = True

    def player_collide(self):
        """If player is hit by something that harms it, decrease its hp, animate a splatter, shake the screen, and
        check if player hp has reached 0 or if the player bashed all enemies to death"""
        s = Splatter(self.player.rect.center)
        s.create_screenshake()
        self.player.hp -= 1
        self.check_lose()
        self.check_win()
        self.player_hit = True      # needed to create a red flash on the screen

    def hit_detection(self):
        """
        Calculate all collisions and what to do when things collide

        Note: "group collide" creates a dictionary w/ key being a sprite from 1st group and value being a list of all sprites
        from 2nd group key sprite collided w/
        "sprite" collide creates a list of all sprites from the second group
        """
        enemy_hit = collision_group(self.ENEMIES, self.BITS_FRIENDLY, False, True)
        # detects if enemy shot by friendly bit
        if enemy_hit:  # checks if hit_detects is not empty
            for enemy in list(enemy_hit.keys()):
                Splatter(enemy.rect.center)
                enemy.hp -= 1
                if enemy.hp <= 0:
                    enemy.kill()
                    self.ENEMY_COUNT -= 1
                    self.check_win()

        friendly_hit = collision_group(self.FRIENDLIES, self.BITS_HOSTILE, False, True)
        # detects if friendly shot by enemy bit
        if friendly_hit:
            for friendly in list(friendly_hit.keys()):
                Splatter(friendly.rect.center)
                friendly.hp -= 1
                if friendly.hp <= 0:
                    friendly.kill()
                    self.FRIENDLY_COUNT -= 1

        barricade_hit = collision_group(self.BARRICADES_NEUTRAL, self.BITS_NONPIERCING, False, True)
        # delete nonpiercing bits if they collide with neutral barricades; we were planning to add in sniper bits that
        # could pierce barricades but there's a lot already
        barricade_friendly_hit = collision_group(self.BARRICADES_FRIENDLY, self.BITS_HOSTILE, False, True)
        barricade_enemy_hit = collision_group(self.BARRICADES_ENEMY, self.BITS_FRIENDLY, False, True)

        player_hit = pygame.sprite.spritecollide(self.player, self.BITS_HOSTILE, True)
        # detects if player shot by enemy, Boolean (3rd parameter) is whether the second parameter is deleted
        player_enemy_hit = pygame.sprite.spritecollide(self.player, self.ENEMIES, True, pygame.sprite.collide_circle)
        # detects if player collided with enemy, fourth parameter is the hitbox for the player
        if player_hit:                  # checks if hit detect lists are not empty
            self.player_collide()
        if player_enemy_hit:
            self.ENEMY_COUNT -= 1
            self.player_collide()

        try:
            player_shield_bash = pygame.sprite.spritecollide(PLAYER_SHIELD, self.ENEMIES, True)
            if player_shield_bash:
                for enemy in player_shield_bash:
                    Splatter(enemy.rect.center)
                for e_hit in range(len(player_shield_bash)):
                    self.ENEMY_COUNT -= 1
                    self.check_win()
        except NameError:
            pass

        try:
            boss_hit = pygame.sprite.spritecollide(self.boss, self.BITS_FRIENDLY, True)
            # detects if boss shot by friendly bit, needed so that player can't bash boss to death
            if boss_hit:  # checks if hit_detects is not empty
                Splatter(self.boss.rect.center)
                self.boss.hp -= 1
                if self.boss.hp <= 0:
                    self.boss.kill()
                    del self.boss
                    self.BOSS_DEAD = True
                    self.check_win()
        except AttributeError:
            pass

        try:
            boss_bash = pygame.sprite.spritecollide(self.boss, self.FRIENDLIES, True)
            # detects if boss hits friendly
            for friendly in boss_bash:
                Splatter(friendly.rect.center)
                self.FRIENDLY_COUNT -= 1
        except AttributeError:
            pass

        try:
            # detects if boss collides with friendly
            if self.player.rect.colliderect(self.boss.rect):
                self.player_collide()
        except (TypeError, AttributeError) as e:
            pass

    def prep_phase(self):
        while self.PREPPING:
            clock.tick(20)
            for event in pygame.event.get():
                self.quit_loop(event)
                if event.type == pygame.KEYDOWN:
                    self.PREPPING = False
            say_centered("Press any key to begin", 75, WHITE)
            say("WASD to move; Shift to sprint; 1, 2, 3, and Tab for weapons; Mouse to aim and fire", int(HEIGHT // 32), WHITE, WIDTH / 2, HEIGHT * 3 / 4)
            say("Esc to quit; lives in top right; enemies left in bottom right", int(HEIGHT // 32), WHITE, WIDTH / 2, HEIGHT * 4 / 5)
            pygame.display.flip()

    def spawn_boss_spawnpoint(self):
        self.boss_sp = SpawnPoint(self.player)
        self.ALL_SPRITES.add(self.boss_sp)
        self.BATTLE_SPRITES.add(self.boss_sp)

    def spawn_boss(self):
        THUNDER_SOUND.play()
        load_music("Music2.ogg")
        screenshake = Splatter(self.boss_sp.rect.center)
        screenshake.create_screenshake()
        screenshake.extend()
        self.boss = Boss(self.boss_sp.rect.center)
        self.ALL_SPRITES.add(self.boss)
        self.BATTLE_SPRITES.add(self.boss)

    """
    ____________________________________________________________________________________________________________________
    BATTLE LOOP: ELIMINATION
    ____________________________________________________________________________________________________________________
    """

    def battle_phase_elimination(self):
        self.spawn_units_recursive(Enemy, ENEMY_AMOUNT - self.ENEMY_COUNT)
        self.spawn_units_recursive(Friendly, FRIENDLY_AMOUNT - self.FRIENDLY_COUNT)
        self.spawn_all_barricades(Barricade, BARRICADE_AMOUNT)
        self.spawn_border()
        if HARDMODE_ON:
            self.spawn_boss_spawnpoint()

        # Main game loop
        while self.PLAYER_ALIVE:
            clock.tick(FPS)
            self.player_hit = False     # used to fill screen with red if player is hit during the frame

            # process input (events)

            for unit in self.UNITS:
                unit.fire()

            try:
                self.boss.fire()
                self.boss.change_type()
            except AttributeError:
                pass

            for event in pygame.event.get():
                self.quit_loop(event)
                # if event.type == pygame.MOUSEBUTTONUP:
                #     self.player.shoot_single()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        self.player.switch_weap()

            # update
            self.ALL_SPRITES.update()  # maps the update() function over ALL_SPRITES list
            self.hit_detection()

            # draw
            screen.fill(GRAY)
            if self.player_hit:
                screen.fill(RED)
            if self.GAME_OVER_ON:
                screen.fill(GRAY)
            self.ALL_SPRITES.draw(screen)
            say(str(self.ENEMY_COUNT), 20, RED, WIDTH - 30, HEIGHT - 30)
            say(str(self.player.hp), 20, BLUE, WIDTH - 15, 10)
            if self.FINAL_STAGE:
                try:
                    say(str(self.boss.hp), 20, RED, 25, 10)
                except AttributeError:
                    pass

            pygame.display.flip()

            self.prep_phase()

    """
    ____________________________________________________________________________________________________________________
    WIN LOOP
    ____________________________________________________________________________________________________________________
    """
    def win(self):
        APPLAUSE_SOUND.play()
        while self.WIN_ON:
            clock.tick(MENU_FPS)  # limit how fast the loop runs

            for event in pygame.event.get():
                self.quit_loop(event)
                self.check_respawn(event)

            # update
            self.WIN_SPRITES.update()

            # draw
            say_centered("W E L L   D O N E.", 100, WHITE)
            say("YOU WON.", 100, WHITE, WIDTH / 2, HEIGHT / 4)
            say("Press enter to restart", int(HEIGHT // 16), WHITE, WIDTH / 2, HEIGHT * 3 / 4)
            self.WIN_SPRITES.draw(screen)
            pygame.display.flip()  # "Flips blackboard," updates display MUST DO AFTER ALL COMPUTATIONS (LAST)

    """
    ____________________________________________________________________________________________________________________
    GAME OVER LOOP
    ____________________________________________________________________________________________________________________
    """

    def check_respawn(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.respawn()
                load_music("Music1.wav")

    def respawn(self):
        self.ENEMY_COUNT = 0
        self.FRIENDLY_COUNT = 0
        for sprite in self.ALL_SPRITES:
            if sprite != self.player:
                sprite.kill()
        self.player.hp = PLAYER_HP
        self.PLAYER_ALIVE = True
        self.player.rect.center = (WIDTH / 2, 3 * HEIGHT / 4)  # sets position of rectangle
        self.GAME_OVER_ON = False
        self.WIN_ON = False
        self.FINAL_STAGE = False
        self.BOSS_DEAD = False
        try:
            del self.boss
        except AttributeError:
            pass
        if self.player.weapon == 1:
            self.player.shield_counter = 0
            self.player.spawn_p_shield()

    def spawn_gofb(self, color):
        fb = FallingBlock(color, 7.5, self.go_speed)
        self.GAME_OVER_SPRITES.add(fb)
        self.GO_COUNT += 1
        self.go_wait *= .9  # spawns falling blocks faster and faster
        self.go_speed += 1

    def game_over(self):
        self.go_speed = GO_SPEED
        self.go_wait = GO_WAIT

        while self.GAME_OVER_ON:
            clock.tick(MENU_FPS)  # limit how fast the loop runs
            if self.GO_COUNT < GO_AMOUNT:
                if self.wt_go.wait_over(self.go_wait):
                    self.spawn_gofb(RED)

            for event in pygame.event.get():
                self.quit_loop(event)
                self.check_respawn(event)

            # update
            self.GAME_OVER_SPRITES.update()

            # draw
            say_centered("GAME OVER. OOF.", 100, WHITE)
            say("Press enter to restart", int(HEIGHT // 16), WHITE, WIDTH / 2, HEIGHT * 3 / 4)
            self.GAME_OVER_SPRITES.draw(screen)
            pygame.display.flip()  # "Flips blackboard," updates display MUST DO AFTER ALL COMPUTATIONS (LAST)










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

    def prep_phase_2_p(self):
        while self.PREPPING:
            clock.tick(20)
            for event in pygame.event.get():
                self.quit_loop(event)
                if event.type == pygame.KEYDOWN:
                    self.PREPPING = False
            say_centered("Press any key to begin", 75, WHITE)
            say("Player 1 (RED): WASD to move, T and Y to aim", int(HEIGHT // 32), WHITE, WIDTH / 2, HEIGHT * 3 / 4)
            say("Player 2 (BLUE): Arrow Keys to move, Shift and Enter to aim", int(HEIGHT // 32), WHITE, WIDTH / 2, HEIGHT * 4 / 5)
            say("Esc to quit; RED health in top left; BLUE health in top right", int(HEIGHT // 32), WHITE, WIDTH / 2, HEIGHT * 5 / 6)
            pygame.display.flip()

    if GAMEMODE == GAMEMODES[2]:
        # Sprite instances and sorting
        player1 = Player2P(RED, 100, 300, TEAMS[0])
        player2 = Player2P(BLUE, 900, 300, TEAMS[1])  # create instance of Player class

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
            say(str(self.player1.hp), 20, RED, 25, 10)
            say(str(self.player2.hp), 20, BLUE, WIDTH - 15, 10)

            self.ALL_SPRITES.draw(screen)

            for event in pygame.event.get():
                self.quit_loop(event)
                if self.DUEL_OVER:
                    self.check_respawn_2_p(event)
            pygame.display.flip()

            self.prep_phase_2_p()

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









"""
________________________________________________________________________________________________________________________
EXECUTION
________________________________________________________________________________________________________________________
"""


def game_loop():
    global game
    game = GAME()
    game.main_menu()
    if GAMEMODE != GAMEMODES[2]:
        load_music("Music1.wav")
    else:
        load_music("Music2.ogg")
    while game.GAME_ON:
        if GAMEMODE == GAMEMODES[1]:
            game.battle_phase_elimination()
        elif GAMEMODE == GAMEMODES[2]:
            game.battle_phase_2_player_duel()
        elif GAMEMODE == GAMEMODES[0]:
            game.battle_phase_elimination()
        MINIGUN_SOUND.stop()
        SHOTGUN_BOSS_SOUND.stop()
        if game.WIN_ON:
            game.win()
        else:
            game.game_over()  # if user hasn't clicked the red x then PLAYER_ALIVE will be reset and game will restart

    if not(QUIT):
        pygame.quit()
        # replay()

    pygame.quit()


game_loop()
