import pygame
import random
import sys
import os

pygame.init()
pygame.display.set_caption("DOOM -1")
pygame.display.set_icon(pygame.image.load("data/backgrounds/doom.ico"))
pygame.key.set_repeat(200, 70)

WIDTH = 800
HEIGHT = 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60
LEFT = 1


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((1, 1))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
main_menu = pygame.sprite.Group()
death_screen = pygame.sprite.Group()

fon = pygame.sprite.Sprite()
fon.image = pygame.transform.scale(load_image("backgrounds\doom_fon.jpg"), (WIDTH, HEIGHT))
fon.rect = fon.image.get_rect()
main_menu.add(fon)

death_bckg = pygame.sprite.Sprite()
death_bckg.image = load_image("backgrounds\death_bckg.png")
death_bckg.rect = death_bckg.image.get_rect()
death_screen.add(death_bckg)

fon2 = pygame.sprite.Sprite()
fon2.image = load_image("backgrounds/fon2.jpg")
fon2.rect = fon2.image.get_rect()
all_sprites.add(fon2)

player = load_image("player\player.png", -1)
reload_sound = pygame.mixer.Sound("data\sounds\Reload.wav")
reload_sound.set_volume(0.3)
player_shoot = load_image("player\player_shoot.png", -1)
death = load_image("death\dead.png", -1)
death_sound = pygame.mixer.Sound("data\sounds\death.wav")
death_sound.set_volume(0.1)
bell_sound = pygame.mixer.Sound("data\sounds\BELLTOLL.wav")
bell_sound.set_volume(0.1)
score = 0

enemy = load_image("enemies\enemy.png", -1)
enemy = pygame.transform.scale(enemy, (40, 105))
enemy_dead = load_image("death\dead_enemy.png", -1)
enemy_dead = pygame.transform.scale(enemy_dead, (105, 40))
enemy_bullet = load_image("Bullets\Bullet_enemy.png", -1)
enemy_bullet = pygame.transform.scale(enemy_bullet, (13, 13))
enemy_bullet_sound = pygame.mixer.Sound("data\sounds\shot.wav")
enemy_bullet_sound.set_volume(0.2)
new_enemy_speed = 0

bullet_player = load_image("Bullets\Bullet.png", -1)
player_bullet_sound = pygame.mixer.Sound("data\sounds\shot2.wav")
player_bullet_sound.set_volume(0.2)
bullet_player = pygame.transform.scale(bullet_player, (13, 13))


class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        if x1 == x2:
            self.add(vertical_borders)
            self.image = pygame.Surface([0, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 0])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(player_group)
        self.add(all_sprites)
        self.image = player
        self.rect = pygame.Rect((400, 510), (126, 128))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = 400
        self.rect.y = 510
        self.images = []
        self.images.append(load_image("player\pgo_1.png", -1))
        self.images.append(load_image("player\pgo_2.png", -1))
        self.images.append(load_image("player\pgo_3.png", -1))
        self.images.append(load_image("player\pgo_4.png", -1))
        self.images_right = self.images
        self.images_left = [pygame.transform.flip(image, True, False) for image in self.images]
        self.index = 0
        self.image = player
        self.velocity = pygame.math.Vector2(0, 0)
        self.animation_frames = 4
        self.current_frame = 0
        self.shooting = False

    def update_frame(self):
        if self.velocity.x == 0:
            if self.shooting:
                self.image = player_shoot
                self.mask = pygame.mask.from_surface(self.image)
            else:
                self.image = player
                self.mask = pygame.mask.from_surface(self.image)
            self.current_frame = 0
            self.index = 0
        else:
            if self.velocity.x > 0:
                self.images = self.images_left
            elif self.velocity.x < 0:
                self.images = self.images_right

            self.current_frame += 1
            if self.current_frame >= self.animation_frames:
                self.current_frame = 0
                self.index = (self.index + 1) % len(self.images)
                self.image = self.images[self.index]
                self.mask = pygame.mask.from_surface(self.image)
            self.rect.move_ip(*self.velocity)

    def update(self):
        if not paused:
            self.update_frame()
            if self.rect.x < 20 and pygame.sprite.spritecollideany(self, vertical_borders):
                self.rect.x += 4
            if self.rect.x > 720 and pygame.sprite.spritecollideany(self, vertical_borders):
                self.rect.x -= 4
        else:
            pygame.sprite.spritecollide(self, enemy_group, True)
            pygame.sprite.spritecollide(self, enemy_bullets, True)

    def shoot(self):
        self.image = player_shoot
        self.mask = pygame.mask.from_surface(self.image)
        PlayerBullets(self.rect.centerx + 2, self.rect.bottom - 95)


class PlayerBullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(player_bullets)
        self.add(all_sprites)
        self.image = bullet_player
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speed = -5

    def update(self):
        self.rect.y += self.speed
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.kill()
        if pygame.sprite.spritecollide(self, enemy_bullets, True):
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.image = enemy
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        while pygame.sprite.spritecollideany(self, enemy_group):
            self.rect.x = random.randrange(WIDTH - 50)
        if pygame.sprite.spritecollideany(self, vertical_borders) and self.rect.x < 25:
            self.rect.x += 25
        elif pygame.sprite.spritecollideany(self, vertical_borders) and self.rect.x > 725:
            self.rect.x -= 25
        self.rect.y = -20
        self.speed = 1
        self.add(enemy_group)

    def update(self, *args):
        global paused
        global new_enemy_speed
        global score
        self.rect.y += self.speed
        if args and args[0].type == ENEMY_SHOOTING_EVENT:
            self.shoot()
        if self.rect.y > HEIGHT:
            self.kill()
        if pygame.sprite.collide_mask(self, player1) and self.image != enemy_dead:
            self.kill()
            paused = True
            player1.image = death
            player1.rect.y = player1.rect.y + 40
            death_sound.play()
        if pygame.sprite.spritecollide(self, enemy_bullets, True):
            self.speed = 0
            if self.image != enemy_dead:
                self.image = enemy_dead
                self.rect = pygame.Rect((self.rect.x, self.rect.y), (154, 54))
                self.mask = pygame.mask.from_surface(self.image)
            else:
                self.kill()
        if pygame.sprite.spritecollide(self, player_bullets, True):
            self.speed = 0
            if self.image != enemy_dead:
                self.image = enemy_dead
                self.rect = pygame.Rect((self.rect.x, self.rect.y), (154, 54))
                self.mask = pygame.mask.from_surface(self.image)
                score += 1
                if score % 10 == 0:
                    new_enemy_speed += 1
            else:
                self.kill()

    def shoot(self):
        if self.image != enemy_dead:
            EnemyBullets(self.rect.centerx + 26, self.rect.bottom - 40)


class EnemyBullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(enemy_bullets)
        self.add(all_sprites)
        self.image = enemy_bullet
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.bottom = y
        self.rect.centerx = x
        self.speed = 2

    def update(self):
        global paused
        global new_enemy_speed
        self.rect.y += self.speed + new_enemy_speed
        if pygame.sprite.collide_mask(self, player1):
            paused = True
            player1.image = death
            death_sound.play()
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.kill()


def terminate():
    pygame.quit()
    sys.exit()


class Button(pygame.sprite.Sprite):
    def __init__(self, group, image, x, y):
        super().__init__(group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.click = False

    def update(self, *args):
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and \
                self.rect.collidepoint(args[0].pos):
            self.click = True


def start_screen():
    pygame.mixer.music.load('data/sounds/start_screen.mp3')
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)
    button = Button(main_menu, load_image("backgrounds\Button.jpg", -1), 289, 570)
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif button.click:
                pygame.mixer.music.stop()
                return
        main_menu.draw(screen)
        main_menu.update(event)
        pygame.display.flip()
        clock.tick(FPS)


start_screen()
clock = pygame.time.Clock()
running = True
deadman = False
player1 = Player()
reload_sound.play()
SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 3000)
ENEMY_SHOOTING_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(ENEMY_SHOOTING_EVENT, 2500)
DEADMAN_EVENT = pygame.USEREVENT + 3
pygame.time.set_timer(DEADMAN_EVENT, 4000)
paused = False
Border(0, 0, WIDTH, 0)
Border(0, HEIGHT, WIDTH, HEIGHT)
Border(1, 1, 1, HEIGHT)
Border(WIDTH - 20, 20, WIDTH - 20, HEIGHT)
death_button = Button(death_screen, load_image("backgrounds\Button2.png", -1), 350, 360)
for _ in range(3):
    enemies = Enemy()
pygame.mixer.music.load('data/sounds/eternal.mp3')
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1)
while running:
    pygame.mouse.set_visible(False)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == SPAWN_EVENT:
            for _ in range(3):
                enemies = Enemy()
        elif event.type == ENEMY_SHOOTING_EVENT:
            enemy_group.update(event)
            enemy_bullet_sound.play()
        elif event.type == DEADMAN_EVENT:
            if paused:
                deadman = True
                bell_sound.play()
        if not paused:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                player1.shooting = True
                player1.shoot()
                player_bullet_sound.play()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    player1.velocity.x = -4
                if event.key == pygame.K_d:
                    player1.velocity.x = 4
            elif event.type == pygame.KEYUP:
                player1.shooting = False
                if event.key == pygame.K_a:
                    player1.velocity.x = 0
                if event.key == pygame.K_d:
                    player1.velocity.x = 0
        else:
            pygame.time.set_timer(ENEMY_SHOOTING_EVENT, 0)
            pygame.time.set_timer(SPAWN_EVENT, 0)
            screen.fill(pygame.Color(0, 0, 0))
    if not deadman:
        screen.fill(pygame.Color(0, 0, 0))
        all_sprites.draw(screen)
        all_sprites.update()
        f1 = pygame.font.Font(None, 36)
        text1 = f1.render(f"УБИТО: {score}", True,
                          (180, 0, 0))
        screen.blit(text1, (10, 10))
    else:
        pygame.mixer.music.stop()
        pygame.mouse.set_visible(True)
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if death_button.click:
                terminate()
        death_screen.draw(screen)
        death_screen.update(event)
    pygame.display.flip()
    clock.tick(FPS)