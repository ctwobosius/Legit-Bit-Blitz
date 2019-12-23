import os
import pygame
import random
import math
from Variables import *     # imports everything from Variables.py without having to use dot notation


PI = math.pi
game_directory = os.path.dirname(__file__)  # ensures game directory reference is always correct
graphics_directory = os.path.join(game_directory, "GFX")  # sets up the graphics directory within the game directory
sound_directory = os.path.join(game_directory, "AUDIO")  # sets up the graphics directory within the game directory


"""
________________________________________________________________________________________________________________________
# Startup Functions
________________________________________________________________________________________________________________________
"""


def startup():
    global screen
    global clock
    pygame.init()           # initialize game
    pygame.mixer.init()     # initialize audio
    pygame.font.init()      # initialize font
    pygame.display.set_caption("Legit Bit Blitz")                           # set top bar title
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)    # set screen dimensions
    clock = pygame.time.Clock()         # used in frame rate limit and checking time


def choose_resolution():
    global HEIGHT
    global WIDTH
    print("Choose the width (we've only tested widths 1080):")
    print()
    try:
        WIDTH = int(input("WIDTH: >> "))
        print()
        print("Choose the height (we've only tested heights 720)")
        HEIGHT = int(input("HEIGHT: >> "))
        print()
    except ValueError:
        HEIGHT = 720
        WIDTH = 1080 


def choose_bit_speed(do_intro=True):
    global SHOTGUN_AMOUNT
    global BIT_SPEED
    if do_intro:
        print("Choose HOW FAST BITS ARE SHOT. The faster they are, the harder it is to dodge. ")
        if GAMEMODE != GAMEMODES[2]:
            print("You should have a minimum of 5. (5 = Slow, 10 = Medium, 15 = Fast):")
        elif GAMEMODE == GAMEMODES[2]:
            print("You should have a minimum of 4. (4 = Slow, 5 = Medium, 6 = Fast):")
        print()
        do_intro = False
    try:
        BIT_SPEED = float(input("BIT SPEED: >> "))
        print()
    except ValueError:
        print("Shake my head, enter a  N U M B E R, try again")
        choose_bit_speed(do_intro)
    BIT_SPEED *= FPS / 60
    if BIT_SPEED < 10:
        SHOTGUN_AMOUNT += 5
        if BIT_SPEED < 5:
            SHOTGUN_AMOUNT += 5


def choose_player_speed(do_intro=True):
    global PLAYER_SPEED
    if do_intro:
        print("Choose HOW FAST THE PLAYERS MOVE. You must enter a number, and should have a minimum of 2. ")
        if GAMEMODE != GAMEMODES[2]:
            print("(2 = Slow, 3 = Medium, 4 = Fast) By the way, we WILL round decimals. Decimals seem to mess up the" +
                  " camera for some unknown reason.")
        if GAMEMODE == GAMEMODES[2]:
            print("(3 = Slow, 5 = Medium, 7 = Fast) By the way, we WILL round decimals.")
        print()
        do_intro = False

    try:
        PLAYER_SPEED = int(input("PLAYER SPEED: >> "))
        print()
    except ValueError:
        print("What part of NUMBER implies that you should enter a WORD???")
        choose_player_speed(do_intro)
    PLAYER_SPEED *= FPS / 60


def ask_number_of(variable, do_intro=True):
    if do_intro:
        print("How many {} would you like?".format(variable.upper()))
        if variable == "enemies":
            print("I'd say start with 30 and work your way up.")
            print("You can put 0 to test out controls, but you'll need to restart to change the number of enemies")
        if variable == "friendlies":
            print("I see you considering having your friendlies outnumber your enemies. You gutless, invertebrate you.")
        print()

    while True:
        answer = input("NUMBER OF {}: >> ".format(variable.upper()))

        if answer == "":
            print("You must really like pressing enter. Go ahead. Try it again.")
        else:
            try:
                value = float(answer)
                if value.is_integer():
                    break
                else:
                    print("If I counted you as half a human, that would be incorrect. Put a whole number, homosapien.")

            except ValueError:
                print("Words do NOT equal numbers, try again")

    return int(value)


def choose_hardmode(do_intro=True):
    global HARDMODE_ON
    if do_intro:
        print("Would you like HARDER ENEMIES (friendlies are also upgraded)?")
        print("(enter 0 or 1, with 0 being \"no\" and 1 being \"yes\")")
        print()
        do_intro = False

    try:
        answer = float(input("HARDMODE ON (0=NO, 1=YES): >> "))
        if answer == 1:
            HARDMODE_ON = True
        elif answer == 0:
            HARDMODE_ON = False
        else:
            print("I said enter 0 or 1. ZERO or ONE. Please read the instructions.")
            choose_hardmode(do_intro)

    except ValueError:
        print("Really? All you have to do is choose between two numbers. TWO NUMBERS. It's not that hard.")
        choose_hardmode(do_intro)


def choose_gamemode(do_intro=True):
    global GAMEMODE
    if do_intro:
        print("WHICH GAMEMODE? (enter 0, 1, or 2, with 0 being \"capture\", 1 being \"elimination\", and 2 being " +
              "\"2 player duel\")")
        print("If you want a description of each gamemode, press 3.")
        print("Actually, there is no capture. We didn't feel like creating it.")
        print()
        do_intro = False

    try:
        answer = float(input("GAMEMODE (1-Single_Player, 2-Two_Player, 3-Description_Of_Gamemodes): >> "))
        if answer == 0:
            print("Wow. If you really want it that badly, go code it yourself!")
            choose_gamemode()
            # GAMEMODE = GAMEMODES[0]
        elif answer == 1:
            GAMEMODE = GAMEMODES[1]
            print()
        elif answer == 2:
            GAMEMODE = GAMEMODES[2]
            print()
        elif answer == 3:
            print("Capture is where you seek to reach the end and capture the red circle.")
            print("Elimination is where you shoot down all the enemies, where the number of enemies alive is in the" +
                  " bottom left. Your lives are in the top right")
            print("2 Player Duel is where two players use one keyboard and try to shoot down each other.")
            print()
            choose_gamemode(do_intro)
        else:
            print("Have you no eyeballs? Enter 0, 1, 2, or 3! Actually, not 0.")
            choose_gamemode(do_intro)

    except ValueError:
        print("Come on. Do some quick maths. 0 + 1 + 2 + 3 don't equal ABC.")
        choose_gamemode(do_intro)


def replay():
    global re_play
    print("Replay? (y/n)")
    answer = str(input()).lower()
    if answer == "n":
        re_play = False
    elif answer == "y":
        re_play = True
    else:
        print("Is it that hard to choose between two letters? Try again")
        replay()

    if re_play:
        choose_resolution()
        choose_bit_speed()
        startup()
        
        
def load_music(file):
    pygame.mixer.music.stop()
    pygame.mixer.music.load(os.path.join(sound_directory, file))
    pygame.mixer.music.play(loops=-1)


def load_sound(filename):
    return pygame.mixer.Sound(os.path.join(sound_directory, filename))


"""
________________________________________________________________________________________________________________________
# Misc. Functions
________________________________________________________________________________________________________________________
"""


def random_direction():
    if random.randrange(0, 2) == 0:
        return -1
    else:
        return 1


def pick_one(x, y):
    if random.randrange(0, 2) == 0:
        return x
    else:
        return y


def determine_decimal_places(num):
    """Recursive function that tells how many decimal places the number has (eg: .333 has 3 decimal places, so power
    would be 3)"""
    if float(num).is_integer():
        return 0
    else:
        return 1 + determine_decimal_places(num * 10)


def return_bool_probability(probability_it_occurs):
    """takes in a probability (eg: .333 = 33.3% chance it occurs) and does a coin toss type thing that returns true if
    the simulation returns the outcome"""
    power = determine_decimal_places(probability_it_occurs)
    upper_bound = (10 ** power)
    max_outcome = upper_bound * probability_it_occurs
    range_list = range(0, upper_bound)
    choose = random.choice(range_list)
    return choose < max_outcome



def say_centered(text, size, color):
    """Say text at the center of the screen"""
    font = pygame.font.SysFont("Consolas", size)
    screen_text = font.render(text, True, color)
    # create a surface (image) of the text, then blit (draw) this image onto another surface
    text_rect = screen_text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
    screen.blit(screen_text, text_rect)
    # helped by https://stackoverflow.com/questions/23982907/python-library-pygame-centering-text


def say(text, size, color, x, y):
    """Say text at the coordinates (x, y)"""
    font = pygame.font.SysFont("Consolas", size)
    screen_text = font.render(text, True, color)
    s_text_rect = screen_text.get_rect()
    s_text_rect.midtop = (x, y)
    screen.blit(screen_text, s_text_rect)


def collision_group(group1, group2, del_group1, del_group2):
    """Detects collision between group 1 and group 2, with del_group being a bool telling the computer whether to
    delete that instance when it collides; Creates a dictionary with keys being sprites from 1st group and values being
    a list of all sprites from 2nd group key sprite collided with"""
    return pygame.sprite.groupcollide(group1, group2, del_group1, del_group2)


"""
________________________________________________________________________________________________________________________
Misc. Classes
________________________________________________________________________________________________________________________
"""


class WaitTimer():
    """A demonstration of our understanding of pygame's clock"""
    def __init__(self):     # creates a function for what the class should do/what traits it has at startup
        self.last_time = 0      # the time since this function last reported True

    def wait_over(self, ms):
        time_since_last_call_to_clockgettime = clock.get_time()
        # not necessarily the same as self.last_time, rather, it is the time since clock.get_time() was called
        self.last_time += time_since_last_call_to_clockgettime
        if self.last_time >= ms:
            self.last_time = 0
            return True
        else:
            return False
# time delay helped by https://www.reddit.com/r/pygame/comments/5r75q1/how_to_get_each_sprite_to_fire_a_bullet/


class FallingBlock(pygame.sprite.Sprite):
    direction_x = random_direction()
    direction_y = random_direction()

    def __init__(self, color, size, speed):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((size, size))       # create rectangle to be drawn
        self.image.fill(color)                          # fill rectangle
        self.rect = self.image.get_rect()     # create a rect for the sprite, which stores the coordinates and hitboxes
        self.x = pick_one(0, WIDTH)
        self.y = random.randrange(0, HEIGHT)
        self.rect.center = (self.x, self.y)
        self.orig_speed = speed
        self.speed_x = self.direction_x * random.randrange(MIN_SPEED_PERCENT, MAX_SPEED_PERCENT) / 100 * speed
        self.speed_y = self.direction_y * random.randrange(MIN_SPEED_PERCENT, MAX_SPEED_PERCENT) / 100 * speed

    def random_speed(self):
        """returns a random speed within a certain ratio of the original speed"""
        return self.direction_x * random.randrange(MIN_SPEED_PERCENT, MAX_SPEED_PERCENT) / 100 * self.orig_speed

    def update(self):
        self.rect.x += self.speed_x     # adding the speed variable to the sprite's x coordinates
        self.rect.y += self.speed_y
        if self.rect.left > WIDTH:      # if reach edge
            self.rect.right = 0         # set the right side of sprite to be x position 0
            self.speed_x = self.random_speed()      # set speed randomly again
            self.y = random.randrange(0, HEIGHT)    # set height to random value
        if self.rect.right < 0:
            self.rect.left = WIDTH
            self.speed_x = self.random_speed()
            self.y = random.randrange(0, HEIGHT)
        if self.rect.top > HEIGHT:
            self.rect.bottom = 0
            self.x = random.randrange(0, WIDTH)
            self.speed_y = self.random_speed()
        if self.rect.bottom < 0:
            self.rect.top = HEIGHT
            self.speed_y = self.random_speed()
            self.x = random.randrange(0, WIDTH)


"""
________________________________________________________________________________________________________________________
Execution
________________________________________________________________________________________________________________________
"""
# choose_resolution()
choose_gamemode()
if GAMEMODE != GAMEMODES[2]:
    ENEMY_AMOUNT = ask_number_of("enemies")
    FRIENDLY_AMOUNT = ask_number_of("friendlies")
    choose_hardmode()
choose_bit_speed()
choose_player_speed()
print("Note: press enter to skip the intro")
startup()

"""
________________________________________________________________________________________________________________________
Load images and music
________________________________________________________________________________________________________________________
"""
# images
SPLATTER_LIST = []
for i in range(1, 6):
    filename = "Splatter{}.png".format(i)
    img = pygame.image.load(os.path.join(graphics_directory, filename)).convert()
    SPLATTER_LIST.append(img)

# sounds
SHOOT_SOUND = pygame.mixer.Sound(os.path.join(sound_directory, "SingleShot.wav"))
SHOOT_SOUND.set_volume(0.5)
SHOTGUN_SOUND = pygame.mixer.Sound(os.path.join(sound_directory, "Shotgun.ogg"))
SHOTGUN_BOSS_SOUND = load_sound("ShotgunBoss.ogg")
MINIGUN_SOUND = load_sound("Minigun.ogg")
APPLAUSE_SOUND = load_sound("Applause.wav")
THUNDER_SOUND = load_sound("Thunder.ogg")
PAIN_SOUNDS = []
for i in range(1, 7):
    filename = "Hit{}.wav".format(i)
    PAIN_SOUNDS.append(load_sound(filename))

# music
MUSIC = [i for i in range(3, 6)]
music_index = random.choice(MUSIC)
music_filename = "Music{}.ogg".format(music_index)
load_music(music_filename)
