import pygame
import math

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Квартира 12: Тайная дверь")
clock = pygame.time.Clock()
FPS = 60

font_main = pygame.font.SysFont("Arial", 24)
font_big = pygame.font.SysFont("Arial", 36)
font_small = pygame.font.SysFont("Arial", 18)

COLORS = {
    "bg": (8, 8, 15),
    "floor": (22, 22, 31),
    "wall_bottom": (35, 31, 34),
    "player_skin": (190, 150, 115),
    "player_hair": (30, 22, 20),
    "player_jacket": (35, 55, 75),
    "monster": (8, 5, 12),
    "eyes": (255, 0, 0),
    "door": (54, 40, 38),
    "photo": (130, 115, 85),
    "secret_door": (60, 10, 25),
    "secret_door_frame": (140, 30, 45),
    "ui_bg": (15, 15, 20),
    "shelf": (45, 35, 32),
    "lamp": (180, 160, 80),
    "diary": (110, 90, 70),
    "exit_door": (40, 35, 33),
}

class Character:
    def __init__(self, x, y, is_monster=False):
        self.x = x
        self.y = y
        self.is_monster = is_monster

    @property
    def pos(self):
        return (self.x, self.y)

    @pos.setter
    def pos(self, value):
        self.x, self.y = value

    def get_hitbox(self):
        # Хитбокс чуть смещён, чтобы соответствовать рисунку
        return pygame.Rect(self.x - 12, self.y - 22, 24, 44)

    def colliderect(self, rect):
        return self.get_hitbox().colliderect(rect)

    def draw(self, surface):
        x, y = self.x, self.y
        if self.is_monster:
            pygame.draw.circle(surface, COLORS["monster"], (x, y - 17), 15)
            pygame.draw.rect(surface, COLORS["monster"], (x - 13, y - 17, 26, 34))
            pygame.draw.line(surface, COLORS["monster"], (x - 9, y - 7), (x - 23, y + 15), 3)
            pygame.draw.line(surface, COLORS["monster"], (x + 9, y - 7), (x + 23, y + 15), 3)
            pygame.draw.circle(surface, COLORS["eyes"], (x - 5, y - 19), 3)
            pygame.draw.circle(surface, COLORS["eyes"], (x + 5, y - 19), 3)
            pygame.draw.line(surface, COLORS["monster"], (x - 6, y + 12), (x - 12, y + 25), 3)
            pygame.draw.line(surface, COLORS["monster"], (x + 6, y + 12), (x + 12, y + 25), 3)
        else:
            pygame.draw.circle(surface, COLORS["player_skin"], (x, y - 13), 10)
            pygame.draw.circle(surface, COLORS["player_hair"], (x, y - 19), 9)
            pygame.draw.rect(surface, COLORS["player_hair"], (x - 9, y - 19, 18, 6))
            pygame.draw.rect(surface, COLORS["player_jacket"], (x - 10, y - 3, 20, 19))
            pygame.draw.line(surface, COLORS["player_skin"], (x - 8, y), (x - 15, y + 10), 3)
            pygame.draw.line(surface, COLORS["player_skin"], (x + 8, y), (x + 15, y + 10), 3)
            pygame.draw.line(surface, (20, 20, 25), (x - 5, y + 16), (x - 8, y + 27), 3)
            pygame.draw.line(surface, (20, 20, 25), (x + 5, y + 16), (x + 8, y + 27), 3)


class Game:
    def __init__(self):
        self.room = "apartment"
        self.message = "Найди старую фотографию. Нажми E рядом с предметом."
        self.message_timer = 240

        self.has_photo = False
        self.has_found_secret_door = False
        self.has_read_diary = False

        self.light_on = True
        self.game_over = False
        self.ending = ""

        self.monster_visible = False
        self.corridor_stay_timer = 0
        self.speed = 2

        self.player = Character(450, 480)
        self.monster = Character(100, 180, is_monster=True)

        # Прямоугольники объектов
        self.photo_rect = pygame.Rect(720, 190, 45, 55)
        self.elevator_rect = pygame.Rect(390, 100, 120, 180)
        self.door_rect = pygame.Rect(730, 350, 100, 150)
        self.secret_door_rect = pygame.Rect(240, 170, 95, 220)
        self.diary_rect = pygame.Rect(420, 330, 60, 40)
        self.secret_room_exit_rect = pygame.Rect(430, 520, 80, 60)
        self.final_door_rect = pygame.Rect(700, 275, 80, 60)  

    def say(self, text, duration=180):
        self.message = text
        self.message_timer = duration

    def move_player(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = self.speed

        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        new_x = self.player.x + dx
        new_y = self.player.y + dy

        new_x = max(20, min(WIDTH - 20, new_x))
        new_y = max(20, min(HEIGHT - 20, new_y))

        self.player.pos = (new_x, new_y)



    def update_monster(self):
        # Если мы на 13 этаже — монстр всегда активен
        if self.room == "floor13":
            self.monster_visible = True

        # Таймер и появление монстра в коридоре оставляем как было
        if self.room == "corridor":
            self.corridor_stay_timer += 1
            if self.corridor_stay_timer >= 600 and not self.monster_visible:
                self.monster_visible = True
                self.monster.pos = (800, 300)
                self.say("Ты слышишь тяжёлые шаги за спиной...", 240)
        else:
            # Если не в коридоре и не на 13 этаже — сбрасываем видимость
            if self.room != "floor13":
                self.corridor_stay_timer = 0
                self.monster_visible = False

        # Движение монстра, если он виден
        if self.monster_visible:
            dx = self.player.x - self.monster.x
            dy = self.player.y - self.monster.y
            dist = math.hypot(dx, dy)

            if dist > 0:
                move_speed = 2.5
                if dist < 150:
                    move_speed = 4.0
                self.monster.x += (dx / dist) * move_speed
                self.monster.y += (dy / dist) * move_speed

            if self.player.colliderect(self.monster.get_hitbox()):
                self.game_over = True
                self.ending = "МОНСТР ПОЙМАЛ ТЕБЯ!"

    def handle_keydown(self, event):
        if self.game_over and event.key == pygame.K_r:
            self.restart_game()
            return
        if self.game_over:
            return  # Пока не нажали R — не обрабатываем другие клавиши

        if event.key == pygame.K_f:
            self.light_on = not self.light_on
            if self.light_on:
                self.say("Фонарик включён. Теперь видно чуть дальше.", 120)
            else:
                self.say("Фонарик выключен. Стало очень темно.", 120)

        if event.key == pygame.K_e:
            if self.room == "apartment":
                dist = math.hypot(self.player.x - self.photo_rect.centerx,
                                  self.player.y - self.photo_rect.centery)
                if dist < 45:
                    self.has_photo = True
                    self.say("На фото ты видишь себя... на 13 этаже!", 240)
                    if not self.has_found_secret_door:
                        self.say("Что-то в коридоре стало другим...", 180)
                elif self.player.colliderect(self.elevator_rect):
                    self.room = "corridor"
                    self.player.pos = (450, 480)
                    self.say("Лифт открылся. В коридоре кто-то есть...", 240)
                else:
                    self.say("Здесь ничего не происходит.", 120)

            elif self.room == "corridor":
                if self.has_photo and self.player.colliderect(self.secret_door_rect):
                    if self.has_found_secret_door and not self.has_read_diary:
                        self.room = "secret_room"
                        self.player.pos = (450, 480)
                        self.say("Ты вошёл в тайную комнату.", 240)
                    elif not self.has_found_secret_door:
                        self.has_found_secret_door = True

                elif self.player.colliderect(self.elevator_rect):
                    if self.has_photo:
                        self.room = "floor13"
                        self.player.pos = (450, 480)
                        self.monster.pos = (100, 120)      # позиция монстра на этаже
                        self.monster_visible = True       # монстр сразу виден
                        self.say("13 этаж. Но как ты сюда попал?", 240)
                    else:
                        self.say("Сначала найди фотографию!", 180)
                elif self.player.colliderect(self.door_rect):
                    self.room = "apartment"
                    self.player.pos = (450, 480)
                    self.say("Ты вернулся в квартиру.", 180)
                else:
                    self.say("Здесь ничего не происходит.", 120)

            elif self.room == "secret_room":
                if self.player.colliderect(self.diary_rect) and not self.has_read_diary:
                    self.has_read_diary = True
                    self.say("В дневнике написано: «13 этаж — это петля. Выход там, где вход.»", 240)
                elif self.player.colliderect(self.secret_room_exit_rect):
                    self.room = "corridor"
                    self.player.pos = (240, 380)
                    self.say("Ты вышел в коридор.", 180)
                else:
                    self.say("Здесь ничего не происходит.", 120)


            elif self.room == "floor13":
                if event.key == pygame.K_e:
                    # Сначала проверяем, стоит ли игрок у финальной двери
                    if self.player.colliderect(self.final_door_rect):
                        if not self.has_read_diary:
                            self.say("Дверь заперта. Похоже, ключ к ней — в дневнике.", 180)
                        else:
                            # Только если дневник прочитан — запускаем концовку
                            self.game_over = True
                            self.ending = "ТЫ РАСКРЫЛ ТАЙНУ! Петля разорвана."
                    else:
                        # Игрок нажал E, но не у двери
                        self.say("Здесь нет двери, с которой можно взаимодействовать.", 120)
                else:
                    # Любая другая клавиша (или E уже обработали выше) — общая подсказка
                    self.say("Ищи дверь, чтобы раскрыть тайну!", 180)


    def restart_game(self):
        self.room = "apartment"
        self.player.pos = (450, 480)
        self.monster.pos = (100, 180)

        self.has_photo = False
        self.has_found_secret_door = False
        self.has_read_diary = False

        self.light_on = True
        self.monster_visible = False
        self.corridor_stay_timer = 0

        self.game_over = False
        self.ending = ""

        self.message = "Найди старую фотографию. Нажми E рядом с предметом."
        self.message_timer = 240

    # --- отрисовка ---

    def draw_background(self, surface):
        surface.fill(COLORS["bg"])
        pygame.draw.rect(surface, COLORS["floor"], (0, 0, WIDTH, 390))
        pygame.draw.rect(surface, COLORS["wall_bottom"], (0, 390, WIDTH, 210))
        for x in range(0, WIDTH, 90):
            pygame.draw.line(surface, (53, 46, 47), (450, 390), (x, HEIGHT), 2)
        pygame.draw.line(surface, (75, 66, 66), (0, 390), (WIDTH, 390), 4)
        pygame.draw.line(surface, (35, 35, 43), (80, 0), (80, 390), 4)
        pygame.draw.line(surface, (35, 35, 43), (820, 0), (820, 390), 4)

    def draw_apartment(self, surface):
        self.draw_background(surface)
        pygame.draw.rect(surface, (12, 22, 38), (100, 65, 150, 180))
        pygame.draw.rect(surface, (100, 100, 120), (100, 65, 150, 180), 2)
        pygame.draw.line(surface, (90, 90, 110), (175, 65), (175, 245), 2)
        pygame.draw.line(surface, (90, 90, 110), (100, 155), (250, 155), 2)

        pygame.draw.rect(surface, COLORS["door"], (390, 200, 110, 190))
        pygame.draw.circle(surface, (190, 150, 70), (475, 295), 5)
        pygame.draw.rect(surface, COLORS["photo"], self.photo_rect)
        pygame.draw.rect(surface, (205, 190, 160), self.photo_rect, 2)

        text_e = font_main.render("E", True, (255, 255, 255))
        surface.blit(text_e, text_e.get_rect(center=self.photo_rect.center))

        text_title = font_big.render("КВАРТИРА 12", True, (255, 255, 255))
        surface.blit(text_title, (30, 25))

        text_hint = font_small.render("Найди фотографию", True, (255, 255, 255))
        surface.blit(text_hint, (650, 155))

    def draw_corridor(self, surface):
        self.draw_background(surface)
        # Стены коридора
        pygame.draw.rect(surface, (5, 5, 12), (350, 80, 200, 310))
        pygame.draw.rect(surface, (90, 75, 70), (350, 80, 200, 310), 2)

        door_w, door_h = 65, 220
        for x in (130, 260, 590, 720):
            pygame.draw.rect(surface, (39, 34, 38), (x, 170, door_w, door_h))
            pygame.draw.rect(surface, (85, 75, 72), (x, 170, door_w, door_h), 2)

        # Тайная дверь (видна только после нахождения фото)
        if self.has_photo:
            pygame.draw.rect(surface, COLORS["secret_door"], self.secret_door_rect)
            pygame.draw.rect(surface, COLORS["secret_door_frame"], self.secret_door_rect, 3)
            text_door = font_small.render("ТАЙНАЯ", True, (180, 180, 180))
            surface.blit(text_door, text_door.get_rect(center=self.secret_door_rect.center))
            text_door2 = font_small.render("ДВЕРЬ", True, (180, 180, 180))
            surface.blit(text_door2, text_door2.get_rect(
                center=(self.secret_door_rect.centerx, self.secret_door_rect.centery + 20)))
        else:
            # Замаскированная дверь
            pygame.draw.rect(surface, (45, 35, 35), self.secret_door_rect)
            pygame.draw.line(surface, (60, 50, 50), self.secret_door_rect.topleft,
                             self.secret_door_rect.bottomright, 2)
            pygame.draw.line(surface, (60, 50, 50), self.secret_door_rect.topright,
                             self.secret_door_rect.bottomleft, 2)

        text_floor = font_big.render("12 ЭТАЖ", True, (255, 255, 255))
        surface.blit(text_floor, (25, 25))

        text_lift = font_main.render("ЛИФТ", True, (255, 255, 255))
        surface.blit(text_lift, (415, 290))


    def draw_floor13(self, surface):
        self.draw_background(surface)

        # Стены комнаты 13 этажа
        pygame.draw.rect(surface, (48, 13, 20), (330, 110, 240, 280))
        pygame.draw.rect(surface, (150, 35, 40), (330, 110, 240, 280), 3)

        text_13 = font_big.render("13", True, (255, 0, 0))
        rect_13 = text_13.get_rect(center=(450, 210))
        surface.blit(text_13, rect_13)

        text_msg = font_small.render("ТЫ УЖЕ БЫЛ ЗДЕСЬ", True, (255, 255, 255))
        surface.blit(text_msg, text_msg.get_rect(center=(450, 300)))

        # Финальная дверь
        pygame.draw.rect(surface, (20, 10, 15), self.final_door_rect)          # тёмное полотно
        pygame.draw.rect(surface, (180, 30, 40), self.final_door_rect, 4)      # яркая рамка
        pygame.draw.line(surface, (220, 50, 60),
                         (self.final_door_rect.centerx, self.final_door_rect.top),
                         (self.final_door_rect.centerx, self.final_door_rect.bottom),
                         2)
        pygame.draw.circle(surface, (100, 20, 30),
                            (self.final_door_rect.centerx, self.final_door_rect.centery),
                            8)
        
        # Отрисовка финальной двери только если прочитан дневник
        if self.has_read_diary:
            pygame.draw.rect(surface, COLORS["door"], self.final_door_rect)
            # можно ещё добавить рамку/детали, если хочешь
        else:
            # Опционально: рисуем вместо двери просто стену/замурованный проём
            pygame.draw.rect(surface, (35, 31, 34), self.final_door_rect)  # цвет стены
            pygame.draw.line(surface, (50, 45, 50),
                            (self.final_door_rect.left, self.final_door_rect.top),
                            (self.final_door_rect.right, self.final_door_rect.bottom), 4)
                # Подсказка у двери
        if self.player.colliderect(self.final_door_rect):
            hint_text = font_main.render("Нажми E, чтобы выйти из петли", True, (255, 255, 255))
            hint_rect = hint_text.get_rect(center=(450, 430))
            pygame.draw.rect(surface, COLORS["ui_bg"], hint_rect.inflate(10, 10))
            surface.blit(hint_text, hint_rect)
    def draw_secret_room(self, surface):
        self.draw_background(surface)
        # Помещение тайной комнаты
        pygame.draw.rect(surface, (28, 24, 26), (150, 100, 600, 350))
        pygame.draw.rect(surface, (40, 36, 38), (150, 100, 600, 350), 3)

        # Полки
        for y in (140, 220, 300):
            pygame.draw.rect(surface, COLORS["shelf"], (170, y, 560, 20))
            for bx in (180, 260, 340, 420, 500, 580):
                pygame.draw.rect(surface, (50, 40, 35), (bx, y + 5, 15, 10))

        # Лампа
        pygame.draw.rect(surface, COLORS["lamp"], (430, 140, 40, 60))
        pygame.draw.polygon(surface, COLORS["lamp"], [(410, 140), (470, 140), (440, 100)])

        # Дневник
        pygame.draw.rect(surface, COLORS["diary"], self.diary_rect)
        pygame.draw.rect(surface, (140, 120, 100), self.diary_rect, 2)
        text_diary = font_small.render("ДНЕВНИК", True, (210, 200, 190))
        surface.blit(text_diary, text_diary.get_rect(center=self.diary_rect.center))

        # Выход из тайной комнаты
        pygame.draw.rect(surface, COLORS["exit_door"], self.secret_room_exit_rect)
        pygame.draw.rect(surface, (100, 90, 85), self.secret_room_exit_rect, 3)
        text_exit = font_small.render("ВЫХОД", True, (220, 220, 220))
        surface.blit(text_exit, text_exit.get_rect(center=self.secret_room_exit_rect.center))

        text_room = font_big.render("ТАЙНАЯ КОМНАТА", True, (200, 200, 200))
        surface.blit(text_room, (220, 40))

    def draw_ui(self, surface):
        # Подсказки управления
        text_move = font_small.render("WASD / стрелки — движение", True, (255, 255, 255))
        text_action = font_small.render("E — взаимодействие, F — фонарик", True, (255, 255, 255))
        surface.blit(text_move, (20, 535))
        surface.blit(text_action, (20, 560))

        # Статус предмета
        if self.has_photo:
            text_photo = font_small.render("ФОТОГРАФИЯ: НАЙДЕНА", True, (255, 255, 0))
            surface.blit(text_photo, (620, 25))

        # Сообщение игрока
        if self.message_timer > 0:
            ui_rect = pygame.Rect(100, 490, 700, 35)
            pygame.draw.rect(surface, COLORS["ui_bg"], ui_rect)
            msg_surf = font_main.render(self.message, True, (255, 255, 255))
            msg_rect = msg_surf.get_rect(center=ui_rect.center)
            surface.blit(msg_surf, msg_rect)

        # Экран проигрыша/победы
        if self.game_over:
            over_surf = font_big.render(self.ending, True, (255, 0, 0))
            over_rect = over_surf.get_rect(center=(450, 250))
            surface.blit(over_surf, over_rect)

            restart_text = "Нажми R, чтобы начать заново"
            if self.ending == "ТЫ РАСКРЫЛ ТАЙНУ! Петля разорвана.":
                restart_text = "Ты победил! Нажми R, чтобы сыграть ещё раз."
            elif self.ending == "МОНСТР ПОЙМАЛ ТЕБЯ!":
                restart_text = "Ты проиграл… Нажми R, чтобы попробовать снова."

            restart_surf = font_small.render(restart_text, True, (255, 255, 255))
            restart_rect = restart_surf.get_rect(center=(450, 330))
            surface.blit(restart_surf, restart_rect)

    def draw_flashlight(self, surface):
        if not self.light_on:
            dark_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dark_overlay.fill((0, 0, 0, 220))
            surface.blit(dark_overlay, (0, 0))
            return

        light_radius = 140
        light_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(light_surf, (255, 255, 255, 160), (int(self.player.x), int(self.player.y)), light_radius)

        for r in range(light_radius, light_radius + 60, 15):
            alpha = max(0, 160 - (r - light_radius) * 3)
            pygame.draw.circle(light_surf, (0, 0, 0, alpha), (int(self.player.x), int(self.player.y)), r)

        surface.blit(light_surf, (0, 0))


# --- Игровой цикл ---

game = Game()
running = True

while running:
    dt = clock.tick(FPS)
    game.message_timer = max(0, game.message_timer - 1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            game.handle_keydown(event)

    keys = pygame.key.get_pressed()
    if not game.game_over:
        game.move_player(keys)
        game.update_monster()

    # Отрисовка комнаты
    if game.room == "apartment":
        game.draw_apartment(screen)
    elif game.room == "corridor":
        game.draw_corridor(screen)
    elif game.room == "floor13":
        game.draw_floor13(screen)
    elif game.room == "secret_room":
        game.draw_secret_room(screen)

    game.draw_flashlight(screen)
    game.player.draw(screen)
    if game.monster_visible:
        game.monster.draw(screen)

    game.draw_ui(screen)

    pygame.display.flip()

pygame.quit()