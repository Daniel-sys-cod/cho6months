import pygame
import sys
import os
import math
import random
import asyncio

pygame.init()
pygame.display.set_caption("For Cho — Happy 6th Anniversary")

SCREEN_W, SCREEN_H = 700, 640
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
clock = pygame.time.Clock()
FPS = 60

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPRITE_DIR = os.path.join(BASE_DIR, "sprites")
MAP_DIR = os.path.join(BASE_DIR, "maps")

FONT_BIG = pygame.font.SysFont("comicsansms", 30, bold=True)
FONT_MED = pygame.font.SysFont("comicsansms", 20, bold=True)
FONT_SMALL = pygame.font.SysFont("arial", 15)
FONT_TEXT = pygame.font.SysFont("georgia", 18)

ROSE = (255, 110, 150)
DEEP_ROSE = (216, 68, 108)
PLUM = (91, 58, 82)
CREAM = (255, 251, 245)
GOLD = (255, 210, 125)
WHITE = (255, 255, 255)

PLAYER_SPEED = 3.4
PLAYER_W, PLAYER_H = 42, 58  
FEET_W, FEET_H = 26, 14      


TOWN_BLOCKS = [
    pygame.Rect(35, 395, 310, 100),   
    pygame.Rect(345, 195, 195, 75),   
    pygame.Rect(295, 270, 75, 75),    
    pygame.Rect(490, 280, 75, 115),   
    pygame.Rect(45, 755, 230, 75),    
    pygame.Rect(45, 845, 230, 90),    
    pygame.Rect(195, 190, 45, 150),   
    pygame.Rect(165, 325, 65, 95),    
    pygame.Rect(330, 515, 55, 100),   
    pygame.Rect(350, 600, 65, 115),   
]

HEART_BLOCKS = [
    pygame.Rect(300, 195, 250, 175),  
    pygame.Rect(105, 745, 150, 80),   
    pygame.Rect(195, 225, 45, 150),   
    pygame.Rect(170, 375, 55, 90),    
    pygame.Rect(335, 420, 55, 110),   
    pygame.Rect(350, 545, 70, 120),   
    pygame.Rect(355, 650, 55, 90),    
]


def load_map(name, fallback_color):
    path = os.path.join(MAP_DIR, name)
    if os.path.exists(path):
        try:
            return pygame.image.load(path).convert()
        except Exception:
            pass
    surf = pygame.Surface((581, 1024))
    surf.fill(fallback_color)
    warn = FONT_MED.render(f"missing maps/{name}", True, (120, 40, 40))
    surf.blit(warn, (20, 20))
    return surf


TOWN_MAP = load_map("town.png", (190, 220, 220))
HEART_MAP = load_map("heart.png", (255, 210, 225))

MAPS_FOUND = os.path.exists(os.path.join(MAP_DIR, "town.png")) and \
             os.path.exists(os.path.join(MAP_DIR, "heart.png"))


def _load_sprite(name):
    p = os.path.join(SPRITE_DIR, name)
    if os.path.exists(p):
        try:
            img = pygame.image.load(p).convert_alpha()
            return pygame.transform.smoothscale(img, (PLAYER_W, PLAYER_H))
        except Exception:
            return None
    return None


RAW_FRAMES = {
    "idle_1": _load_sprite("idle_1.png"),
    "idle_2": _load_sprite("idle_2.png"),
    "walk_1": _load_sprite("walk_1.png"),
    "walk_2": _load_sprite("walk_2.png"),
    "walk_3": _load_sprite("walk_3.png"),
    "happy_1": _load_sprite("happy_1.png"),
}
SPRITES_FOUND = all(v is not None for v in RAW_FRAMES.values())

ANIM_IDLE = (["idle_1", "idle_1", "idle_1", "idle_2"], 450)
ANIM_WALK = (["walk_1", "walk_2", "walk_3", "walk_2"], 130)
ANIM_HAPPY = (["happy_1"], 200)


class Animator:
    def __init__(self):
        self.clip_name = None
        self.clip = ANIM_IDLE
        self.index = 0
        self.timer = 0

    def play(self, clip, name):
        if self.clip_name != name:
            self.clip_name, self.clip, self.index, self.timer = name, clip, 0, 0

    def update(self, dt):
        keys, ms = self.clip
        self.timer += dt
        if self.timer >= ms:
            self.timer -= ms
            self.index = (self.index + 1) % len(keys)

    def frame(self):
        keys, _ = self.clip
        return RAW_FRAMES.get(keys[self.index % len(keys)])


def draw_fallback_player(surf, x, y, facing_right, walk_phase, moving):
    step = int(math.sin(walk_phase) * 3) if moving else 0
    cx = x + PLAYER_W // 2
    pygame.draw.ellipse(surf, (0, 0, 0, 60), (x + 8, y + PLAYER_H - 10, PLAYER_W - 16, 8))
    pygame.draw.rect(surf, DEEP_ROSE, (x + 12, y + PLAYER_H - 22, 8, 12 + step))
    pygame.draw.rect(surf, DEEP_ROSE, (x + PLAYER_W - 20, y + PLAYER_H - 22, 8, 12 - step))
    body = pygame.Rect(x + 8, y + 14, PLAYER_W - 16, PLAYER_H - 36)
    pygame.draw.ellipse(surf, ROSE, body)
    pygame.draw.ellipse(surf, WHITE, body, 2)
    pygame.draw.circle(surf, PLUM, (cx - 5, y + 26), 3)
    pygame.draw.circle(surf, PLUM, (cx + 5, y + 26), 3)


letters_data = [
    (110, 300, "THE BEGINNING",
     "The day I met you, my whole life quietly split into 'before you' and 'after you.'"),
    (470, 520, "AN ORDINARY DAY",
     "I don't say it enough, but you are the best thing that has ever happened to me."),
    (300, 660, "A NIGHT I'M NOT PROUD OF",
     "There was a night I let my fear talk louder than my love, and I tried to walk away. I'm sorry."),
    (150, 760, "WHEN I SHUT YOU OUT",
     "I even blocked you once, like that would fix anything. You kept trying anyway."),
    (430, 800, "WHAT YOU TAUGHT ME",
     "Watching you stay when I gave you every reason to leave taught me what real love looks like."),
    (280, 470, "SIX YEARS",
     "Every fight, every cold silence -- you stayed. Thank you for six years of choosing me."),
]

WELL_POS = (185, 545)   
DOOR_POS = (430, 300)   
PORTAL_POS = (150, 850) 

WELL_TEXT = ("Memory Well: even on my worst days, wishing on anything, "
             "I only ever wished for more time with you.")

FINAL_TEXT = (
    "I'm really sorry I forgot our anniversary, baby. I never meant to make you feel "
    "small. I'm sorry for the times I let fear talk me into pulling away -- even trying "
    "to break up with you, even blocking you -- while you kept showing up for me anyway. "
    "I don't deserve how patient you've been, but I promise I'm done taking it for "
    "granted. Will you forgive me?"
)


class Letter:
    def __init__(self, x, y, tag, text):
        self.x, self.y = x, y
        self.tag, self.text = tag, text
        self.collected = False
        self.bob = random.uniform(0, math.pi * 2)


class Particle:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vx = random.uniform(-1.2, 1.2)
        self.vy = random.uniform(-3, -1)
        self.life = 55
        self.color = random.choice([ROSE, GOLD, (201, 162, 255), WHITE])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.life -= 1

    def draw(self, surf, cam_x, cam_y):
        if self.life > 0:
            pygame.draw.circle(surf, self.color, (int(self.x - cam_x), int(self.y - cam_y)), 3)


def draw_letter_icon(surf, x, y, t, seed):
    bob = math.sin(t * 0.005 + seed) * 4
    r = pygame.Rect(x - 14, y - 8 + bob, 28, 18)
    glow = 40 + int(20 * math.sin(t * 0.006 + seed))
    s = pygame.Surface((46, 46), pygame.SRCALPHA)
    pygame.draw.circle(s, (255, 200, 220, glow), (23, 23), 20)
    surf.blit(s, (x - 23, y - 15 + bob))
    pygame.draw.rect(surf, CREAM, r, border_radius=3)
    pygame.draw.rect(surf, ROSE, r, 2, border_radius=3)
    pygame.draw.polygon(surf, ROSE, [(r.left, r.top), (r.right, r.top), (r.centerx, r.centery)])


def draw_glow_marker(surf, x, y, t, color=GOLD, radius=26):
    glow = int(30 + 15 * math.sin(t * 0.005))
    s = pygame.Surface((radius * 3, radius * 3), pygame.SRCALPHA)
    pygame.draw.circle(s, (*color, glow), (radius * 1.5, radius * 1.5), radius)
    surf.blit(s, (x - radius * 1.5, y - radius * 1.5))
    pygame.draw.circle(surf, color, (x, y), 6)


def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.size(test)[0] > max_width:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)
    return lines


def draw_dialogue_box(surf, tag, text):
    box = pygame.Rect(40, SCREEN_H - 150, SCREEN_W - 80, 120)
    pygame.draw.rect(surf, CREAM, box, border_radius=14)
    pygame.draw.rect(surf, ROSE, box, 3, border_radius=14)
    if tag:
        surf.blit(FONT_SMALL.render(tag, True, DEEP_ROSE), (box.x + 16, box.y + 10))
    y0 = box.y + (34 if tag else 16)
    for i, line in enumerate(wrap_text(text, FONT_TEXT, box.width - 32)):
        surf.blit(FONT_TEXT.render(line, True, PLUM), (box.x + 16, y0 + i * 23))
    hint = FONT_SMALL.render("press SPACE to continue", True, (150, 110, 130))
    surf.blit(hint, (box.right - hint.get_width() - 14, box.bottom - 20))


letters = [Letter(*d) for d in letters_data]
particles = []
well_opened = False
door_opened = False

current_map = "town"
player_x, player_y = 190.0, 445.0  # Spawns directly inside the school building
vel_x, vel_y = 0.0, 0.0
facing_right = True
moving = False
anim = Animator()
walk_phase = 0.0

STATE_TITLE, STATE_PLAY, STATE_DIALOGUE, STATE_FADE_OUT, STATE_FADE_IN, \
    STATE_ENDING, STATE_FORGIVE, STATE_END = range(8)
state = STATE_TITLE
active_tag, active_text = "", ""
fade_alpha = 0
achieve_msg, achieve_timer = "", 0
teleport_lines = ["Wait... something's pulling me somewhere else...", "Whoa -- where am I?"]

t = 0


def current_bg():
    return TOWN_MAP if current_map == "town" else HEART_MAP


def show_achievement(msg):
    global achieve_msg, achieve_timer
    achieve_msg, achieve_timer = msg, 220


def open_letter(letter):
    global state, active_tag, active_text
    letter.collected = True
    active_tag, active_text = letter.tag, letter.text
    state = STATE_DIALOGUE
    for _ in range(10):
        particles.append(Particle(letter.x, letter.y))


async def main():
    global running, state, current_map, player_x, player_y, facing_right, moving, walk_phase
    global active_tag, active_text, fade_alpha, well_opened, door_opened, t

    while running:
        dt = clock.tick(FPS)
        t += dt
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if state == STATE_TITLE and event.key == pygame.K_SPACE:
                    state = STATE_PLAY

                elif state == STATE_PLAY and event.key == pygame.K_e:
                    interacted = False
                    if current_map == "heart":
                        near, best = None, 55
                        for L in letters:
                            if L.collected:
                                continue
                            d = math.hypot(L.x - player_x, L.y - player_y)
                            if d < best:
                                best, near = d, L
                        if near:
                            open_letter(near)
                            interacted = True
                        if not interacted and not well_opened:
                            if math.hypot(WELL_POS[0] - player_x, WELL_POS[1] - player_y) < 55:
                                well_opened = True
                                active_tag, active_text = "THE MEMORY WELL", WELL_TEXT
                                state = STATE_DIALOGUE
                                interacted = True
                                show_achievement("\u2728 A secret at the Memory Well.")
                        if not interacted:
                            if math.hypot(DOOR_POS[0] - player_x, DOOR_POS[1] - player_y) < 55:
                                if all(L.collected for L in letters):
                                    door_opened = True
                                    state = STATE_ENDING
                                else:
                                    remaining = sum(1 for L in letters if not L.collected)
                                    active_tag = "CHAMBERS OF AFFECTION"
                                    active_text = f"The door won't open yet. {remaining} more letter(s) are still waiting."
                                    state = STATE_DIALOGUE

                elif state == STATE_DIALOGUE and event.key == pygame.K_SPACE:
                    state = STATE_PLAY

                elif state == STATE_ENDING and event.key == pygame.K_SPACE:
                    state = STATE_FORGIVE

                elif state == STATE_FORGIVE and event.key in (pygame.K_SPACE, pygame.K_y, pygame.K_RETURN):
                    state = STATE_END
                    for _ in range(60):
                        particles.append(Particle(SCREEN_W // 2, SCREEN_H // 2))

        # ---------------- movement ----------------
        if state == STATE_PLAY:
            dx = dy = 0
            if keys[pygame.K_UP] or keys[pygame.K_w]: dy -= 1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy += 1
            if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx -= 1; facing_right = False
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += 1; facing_right = True

            moving = bool(dx or dy)
            if moving:
                length = math.hypot(dx, dy)
                player_x += (dx / length) * PLAYER_SPEED
                player_y += (dy / length) * PLAYER_SPEED
                walk_phase += 0.4
                anim.play(ANIM_WALK, "walk")
            else:
                anim.play(ANIM_IDLE, "idle")

            bg = current_bg()
            player_x = max(20, min(bg.get_width() - 20, player_x))
            player_y = max(20, min(bg.get_height() - 20, player_y))

            if current_map == "town":
                if math.hypot(PORTAL_POS[0] - player_x, PORTAL_POS[1] - player_y) < 40:
                    state = STATE_FADE_OUT
                    fade_alpha = 0

        if state == STATE_FADE_OUT:
            fade_alpha += 6
            if fade_alpha >= 255:
                fade_alpha = 255
                current_map = "heart"
                player_x, player_y = HEART_MAP.get_width() // 2, HEART_MAP.get_height() - 60
                state = STATE_FADE_IN

        elif state == STATE_FADE_IN:
            fade_alpha -= 4
            if fade_alpha <= 0:
                fade_alpha = 0
                state = STATE_PLAY
                show_achievement("Welcome to my heart. Explore around \U0001F49D")

        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)

        if state == STATE_END and random.random() < 0.25:
            particles.append(Particle(random.randint(0, SCREEN_W), -10))

        if achieve_timer > 0:
            achieve_timer -= 1

        anim.update(dt)

        # ---------------- camera ----------------
        bg = current_bg()
        cam_x = max(0, min(bg.get_width() - SCREEN_W, player_x - SCREEN_W // 2))
        cam_y = max(0, min(bg.get_height() - SCREEN_H, player_y - SCREEN_H // 2))
        if bg.get_width() < SCREEN_W:
            cam_x = -(SCREEN_W - bg.get_width()) // 2
        if bg.get_height() < SCREEN_H:
            cam_y = -(SCREEN_H - bg.get_height()) // 2

        # ---------------- draw ----------------
        if state == STATE_TITLE:
            screen.fill((255, 235, 244))
            title1 = FONT_BIG.render("Happy 6th Anniversary", True, DEEP_ROSE)
            title2 = FONT_MED.render("Cho Haythi Chanthi \U0001F49D", True, PLUM)
            sub = FONT_SMALL.render("Walk around for a bit... and see where you end up.", True, PLUM)
            prompt = FONT_MED.render("Press SPACE to start", True, ROSE)
            screen.blit(title1, title1.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 60)))
            screen.blit(title2, title2.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 15)))
            screen.blit(sub, sub.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 25)))
            screen.blit(prompt, prompt.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 90)))
            if not MAPS_FOUND:
                warn = FONT_SMALL.render("(maps/town.png or maps/heart.png missing -- using placeholder)", True, (170, 40, 40))
                screen.blit(warn, warn.get_rect(center=(SCREEN_W // 2, SCREEN_H - 30)))
            if not SPRITES_FOUND:
                warn2 = FONT_SMALL.render("(sprites/ missing -- using placeholder character)", True, (170, 40, 40))
                screen.blit(warn2, warn2.get_rect(center=(SCREEN_W // 2, SCREEN_H - 10)))

        elif state in (STATE_PLAY, STATE_DIALOGUE, STATE_FADE_OUT, STATE_FADE_IN):
            screen.fill((20, 20, 30))
            screen.blit(bg, (-cam_x, -cam_y))

            if current_map == "town":
                draw_glow_marker(screen, PORTAL_POS[0] - cam_x, PORTAL_POS[1] - cam_y, t)
            else:
                for L in letters:
                    if not L.collected:
                        draw_letter_icon(screen, L.x - cam_x, L.y - cam_y, t, L.x + L.y)
                well_col = GOLD if not well_opened else (200, 200, 200)
                draw_glow_marker(screen, WELL_POS[0] - cam_x, WELL_POS[1] - cam_y, t, well_col, 20)
                door_col = GOLD if all(L.collected for L in letters) else (170, 160, 190)
                draw_glow_marker(screen, DOOR_POS[0] - cam_x, DOOR_POS[1] - cam_y, t, door_col, 26)

            for p in particles:
                p.draw(screen, cam_x, cam_y)

            px, py = player_x - cam_x - PLAYER_W // 2, player_y - cam_y - PLAYER_H
            frame = anim.frame()
            if frame is not None:
                img = pygame.transform.flip(frame, True, False) if not facing_right else frame
                screen.blit(img, (px, py))
            else:
                draw_fallback_player(screen, px, py, facing_right, walk_phase, moving)

            if current_map == "heart":
                found = sum(1 for L in letters if L.collected)
                pygame.draw.rect(screen, (255, 255, 255), (12, 12, 170, 34), border_radius=12)
                screen.blit(FONT_MED.render(f"\U0001F48C {found}/{len(letters)}", True, PLUM), (22, 18))

            if achieve_timer > 0:
                msg = FONT_SMALL.render(achieve_msg, True, DEEP_ROSE)
                bg_rect = pygame.Rect(0, 0, msg.get_width() + 24, 32)
                bg_rect.center = (SCREEN_W // 2, 50)
                pygame.draw.rect(screen, (255, 255, 255), bg_rect, border_radius=16)
                screen.blit(msg, msg.get_rect(center=bg_rect.center))

            if state == STATE_DIALOGUE:
                draw_dialogue_box(screen, active_tag, active_text)
            elif state == STATE_PLAY:
                near_msg = None
                if current_map == "heart":
                    for L in letters:
                        if not L.collected and math.hypot(L.x - player_x, L.y - player_y) < 55:
                            near_msg = "Press E to open the letter"
                    if near_msg is None and not well_opened and math.hypot(WELL_POS[0] - player_x, WELL_POS[1] - player_y) < 55:
                        near_msg = "Press E to look in the well"
                    if near_msg is None and math.hypot(DOOR_POS[0] - player_x, DOOR_POS[1] - player_y) < 55:
                        near_msg = "Press E to open the door"
                if near_msg:
                    hint = FONT_SMALL.render(near_msg, True, PLUM)
                    bg_rect = pygame.Rect(0, 0, hint.get_width() + 20, 30)
                    bg_rect.center = (SCREEN_W // 2, 40)
                    pygame.draw.rect(screen, (255, 255, 255), bg_rect, border_radius=14)
                    screen.blit(hint, hint.get_rect(center=bg_rect.center))

            if state in (STATE_FADE_OUT, STATE_FADE_IN):
                s = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                s.fill((255, 235, 244, fade_alpha))
                screen.blit(s, (0, 0))
                if fade_alpha > 120:
                    line = teleport_lines[0] if fade_alpha > 200 else teleport_lines[1]
                    txt = FONT_MED.render(line, True, DEEP_ROSE)
                    screen.blit(txt, txt.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2)))

        elif state == STATE_ENDING:
            screen.fill((255, 235, 210))
            box = pygame.Rect(40, 70, SCREEN_W - 80, SCREEN_H - 140)
            pygame.draw.rect(screen, CREAM, box, border_radius=20)
            pygame.draw.rect(screen, GOLD, box, 4, border_radius=20)
            title = FONT_BIG.render("Cho...", True, DEEP_ROSE)
            screen.blit(title, title.get_rect(center=(SCREEN_W // 2, box.top + 40)))
            for i, line in enumerate(wrap_text(FINAL_TEXT, FONT_TEXT, box.width - 60)):
                screen.blit(FONT_TEXT.render(line, True, PLUM), (box.x + 30, box.top + 80 + i * 25))
            prompt = FONT_SMALL.render("press SPACE to answer", True, ROSE)
            screen.blit(prompt, prompt.get_rect(center=(SCREEN_W // 2, box.bottom - 22)))

        elif state == STATE_FORGIVE:
            screen.fill((255, 235, 210))
            q = FONT_BIG.render("Will you forgive me?", True, DEEP_ROSE)
            screen.blit(q, q.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 60)))
            btn1 = pygame.Rect(0, 0, 190, 54); btn1.center = (SCREEN_W // 2 - 110, SCREEN_H // 2 + 30)
            btn2 = pygame.Rect(0, 0, 230, 54); btn2.center = (SCREEN_W // 2 + 130, SCREEN_H // 2 + 30)
            pygame.draw.rect(screen, ROSE, btn1, border_radius=27)
            pygame.draw.rect(screen, WHITE, btn2, border_radius=27)
            pygame.draw.rect(screen, ROSE, btn2, 3, border_radius=27)
            screen.blit(FONT_MED.render("Yes \U0001F49D", True, WHITE), FONT_MED.render("Yes \U0001F49D", True, WHITE).get_rect(center=btn1.center))
            screen.blit(FONT_MED.render("Yes, I forgive you", True, DEEP_ROSE), FONT_MED.render("Yes, I forgive you", True, DEEP_ROSE).get_rect(center=btn2.center))
            hint = FONT_SMALL.render("press SPACE, ENTER, or Y", True, PLUM)
            screen.blit(hint, hint.get_rect(center=(SCREEN_W // 2, SCREEN_H - 46)))

        elif state == STATE_END:
            screen.fill((255, 240, 245))
            for p in particles:
                p.draw(screen, 0, 0)
            title = FONT_BIG.render("Thank you, Cho \U0001F49D", True, DEEP_ROSE)
            screen.blit(title, title.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 45)))
            for i, line in enumerate(wrap_text(
                    "Six years with you and I still fall for you more every single day. "
                    "Happy anniversary, my love.", FONT_TEXT, SCREEN_W - 140)):
                ls = FONT_TEXT.render(line, True, PLUM)
                screen.blit(ls, ls.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + i * 26)))
            hint = FONT_SMALL.render("ESC to quit", True, PLUM)
            screen.blit(hint, hint.get_rect(center=(SCREEN_W // 2, SCREEN_H - 36)))

        pygame.display.flip()
        await asyncio.sleep(0)  # Required for Pygbag / browser async execution

    pygame.quit()
    sys.exit()

running = True
asyncio.run(main())