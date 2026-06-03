import pygame
import random
import sys
import math

# --- Init ---
pygame.init()
W, H = 600, 500
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("🚀 Space Shooter")
clock = pygame.time.Clock()

# --- Colors ---
BLACK  = (0, 0, 0)
GREEN  = (0, 255, 80)
CYAN   = (0, 255, 255)
RED    = (255, 80, 80)
ORANGE = (255, 170, 0)
PURPLE = (180, 100, 255)
WHITE  = (255, 255, 255)
YELLOW = (255, 255, 0)
DKGREEN= (0, 120, 40)

# --- Font ---
font_big   = pygame.font.SysFont("Courier New", 36, bold=True)
font_med   = pygame.font.SysFont("Courier New", 22, bold=True)
font_small = pygame.font.SysFont("Courier New", 15)

# ──────────────────────────────────────────
class Player:
    def __init__(self):
        self.x = W // 2
        self.y = H - 70
        self.w = 36
        self.h = 36
        self.speed = 5
        self.shoot_cd = 0

    def update(self, keys):
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.x = max(self.w//2, self.x - self.speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.x = min(W - self.w//2, self.x + self.speed)
        if self.shoot_cd > 0: self.shoot_cd -= 1

    def shoot(self):
        if self.shoot_cd <= 0:
            self.shoot_cd = 12
            return Bullet(self.x, self.y - self.h//2)
        return None

    def draw(self, surf):
        # Body
        pts = [(self.x, self.y-18), (self.x+14, self.y+12),
               (self.x+8, self.y+7), (self.x, self.y+10),
               (self.x-8, self.y+7), (self.x-14, self.y+12)]
        pygame.draw.polygon(surf, GREEN, pts)
        # Cockpit
        pygame.draw.circle(surf, CYAN, (self.x, self.y), 5)
        # Engines
        pygame.draw.rect(surf, (0, 180, 220), (self.x-11, self.y+12, 6, 8))
        pygame.draw.rect(surf, (0, 180, 220), (self.x+5,  self.y+12, 6, 8))

    def rect(self):
        return pygame.Rect(self.x - self.w//2, self.y - self.h//2, self.w, self.h)


# ──────────────────────────────────────────
class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 4
        self.h = 14
        self.spd = 10

    def update(self): self.y -= self.spd
    def alive(self):  return self.y > -20

    def draw(self, surf):
        for i in range(self.h):
            alpha = int(255 * (1 - i / self.h))
            color = (0, alpha, alpha)
            pygame.draw.rect(surf, color, (self.x - self.w//2, self.y - self.h + i, self.w, 1))

    def rect(self):
        return pygame.Rect(self.x - self.w//2, self.y - self.h, self.w, self.h)


# ──────────────────────────────────────────
class Enemy:
    def __init__(self, level):
        types = ['basic'] if level < 2 else (['basic','fast'] if level < 3 else ['basic','fast','tank'])
        self.type = random.choice(types)
        self.x = random.randint(24, W - 24)
        self.y = -34

        if self.type == 'basic':
            self.w, self.h = 28, 28
            self.hp = self.max_hp = 1
            self.spd = 1.2 + (level-1)*0.28
            self.pts = 10
            self.col = RED
        elif self.type == 'fast':
            self.w, self.h = 22, 22
            self.hp = self.max_hp = 1
            self.spd = (1.2 + (level-1)*0.28) * 2.1
            self.pts = 20
            self.col = ORANGE
        else:
            self.w, self.h = 40, 38
            self.hp = self.max_hp = 3
            self.spd = (1.2 + (level-1)*0.28) * 0.6
            self.pts = 50
            self.col = PURPLE

    def update(self): self.y += self.spd
    def alive(self):  return self.y < H + self.h

    def draw(self, surf):
        x, y, w, h = int(self.x), int(self.y), self.w, self.h

        if self.type == 'basic':
            pts = [(x, y-h//2), (x+w//2, y+h//2), (x, y+h//4), (x-w//2, y+h//2)]
            pygame.draw.polygon(surf, self.col, pts)

        elif self.type == 'fast':
            pts = [(x, y-h//2), (x+w//3, y+h//2), (x, y), (x-w//3, y+h//2)]
            pygame.draw.polygon(surf, self.col, pts)
            pygame.draw.circle(surf, YELLOW, (x, y), 4)

        else:  # tank
            pygame.draw.rect(surf, self.col, (x-w//2, y-h//2, w, h))
            # HP bar background
            pygame.draw.rect(surf, (60, 60, 60), (x-w//2+3, y+h//2-9, w-6, 5))
            # HP bar fill
            bar_w = int((w-6) * (self.hp / self.max_hp))
            pygame.draw.rect(surf, GREEN, (x-w//2+3, y+h//2-9, bar_w, 5))

    def rect(self):
        return pygame.Rect(self.x - self.w//2, self.y - self.h//2, self.w, self.h)


# ──────────────────────────────────────────
class Particle:
    def __init__(self, x, y, col):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.pi * 2)
        spd   = random.uniform(1, 4)
        self.vx = math.cos(angle) * spd
        self.vy = math.sin(angle) * spd
        self.life = 1.0
        self.col = col

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        self.life -= 0.04

    def alive(self): return self.life > 0

    def draw(self, surf):
        r = max(1, int(3 * self.life))
        c = tuple(min(255, int(v)) for v in self.col)
        pygame.draw.circle(surf, c, (int(self.x), int(self.y)), r)


# ──────────────────────────────────────────
def make_stars():
    return [{'x': random.randint(0, W), 'y': random.randint(0, H),
             'r': random.uniform(0.5, 2), 'spd': random.uniform(0.2, 0.9)}
            for _ in range(90)]

def draw_stars(surf, stars):
    for s in stars:
        bright = int(180 * s['r'] / 2)
        pygame.draw.circle(surf, (bright, bright, min(255, bright+40)),
                           (int(s['x']), int(s['y'])), max(1, int(s['r'])))

def update_stars(stars):
    for s in stars:
        s['y'] += s['spd']
        if s['y'] > H:
            s['y'] = 0
            s['x'] = random.randint(0, W)

def draw_text_center(surf, text, font, color, y):
    img = font.render(text, True, color)
    surf.blit(img, (W//2 - img.get_width()//2, y))

def draw_ui(surf, score, lives, level):
    # Score
    s = font_small.render(f"SCORE: {score}", True, GREEN)
    surf.blit(s, (W//2 - s.get_width()//2, 8))
    # Lives
    l = font_small.render("❤ " * lives, True, GREEN)
    surf.blit(l, (10, 8))
    # Level
    lv = font_small.render(f"LVL {level}", True, GREEN)
    surf.blit(lv, (W - lv.get_width() - 10, 8))


# ──────────────────────────────────────────
def start_screen():
    stars = make_stars()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return

        screen.fill(BLACK)
        draw_stars(screen, stars)
        update_stars(stars)

        draw_text_center(screen, "SPACE SHOOTER", font_big, GREEN, 130)
        draw_text_center(screen, "Arrow Keys / A D  =  Move", font_small, DKGREEN, 210)
        draw_text_center(screen, "SPACE  =  Fire",            font_small, DKGREEN, 235)
        draw_text_center(screen, "3 Qisam ke Dushman",        font_small, DKGREEN, 260)
        draw_text_center(screen, "ENTER ya SPACE dabao",      font_med,   GREEN,   320)

        pygame.display.flip()
        clock.tick(60)


def game_over_screen(score, level):
    stars = make_stars()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return True   # restart
                if event.key == pygame.K_ESCAPE:
                    return False  # quit

        screen.fill(BLACK)
        draw_stars(screen, stars)
        update_stars(stars)

        draw_text_center(screen, "GAME OVER",              font_big,   RED,    150)
        draw_text_center(screen, f"Score:  {score}",       font_med,   CYAN,   220)
        draw_text_center(screen, f"Level:  {level}",       font_med,   WHITE,  255)
        draw_text_center(screen, "ENTER = Phir Khelo",     font_small, DKGREEN,320)
        draw_text_center(screen, "ESC   = Bahar Jao",      font_small, DKGREEN,345)

        pygame.display.flip()
        clock.tick(60)


# ──────────────────────────────────────────
def game_loop():
    player    = Player()
    bullets   = []
    enemies   = []
    particles = []
    stars     = make_stars()

    score          = 0
    lives          = 3
    level          = 1
    spawn_timer    = 0

    while True:
        # ── Events ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        # ── Input ──
        keys = pygame.key.get_pressed()
        player.update(keys)
        if keys[pygame.K_SPACE]:
            b = player.shoot()
            if b: bullets.append(b)

        # ── Spawn enemies ──
        spawn_timer += 1
        spawn_rate = max(28, 80 - level * 8)
        if spawn_timer >= spawn_rate:
            enemies.append(Enemy(level))
            spawn_timer = 0

        # ── Update ──
        for b in bullets:   b.update()
        for e in enemies:   e.update()
        for p in particles: p.update()
        update_stars(stars)

        # ── Bullet vs Enemy ──
        dead_bullets = set()
        dead_enemies = set()
        for bi, b in enumerate(bullets):
            for ei, e in enumerate(enemies):
                if b.rect().colliderect(e.rect()):
                    dead_bullets.add(bi)
                    e.hp -= 1
                    if e.hp <= 0:
                        dead_enemies.add(ei)
                        score += e.pts
                        for _ in range(10):
                            particles.append(Particle(e.x, e.y, e.col))
                    else:
                        for _ in range(4):
                            particles.append(Particle(e.x, e.y, WHITE))

        bullets = [b for i,b in enumerate(bullets) if i not in dead_bullets]
        enemies = [e for i,e in enumerate(enemies) if i not in dead_enemies]

        # ── Enemy exits bottom ──
        remaining = []
        for e in enemies:
            if not e.alive():
                lives -= 1
                for _ in range(14):
                    particles.append(Particle(player.x, player.y, RED))
                if lives <= 0:
                    return score, level   # game over
            else:
                remaining.append(e)
        enemies = remaining

        # ── Cleanup ──
        bullets   = [b for b in bullets   if b.alive()]
        particles = [p for p in particles if p.alive()]

        # ── Level up ──
        new_level = 1 + score // 200
        if new_level != level:
            level = new_level

        # ── Draw ──
        screen.fill(BLACK)
        draw_stars(screen, stars)

        player.draw(screen)
        for b in bullets:   b.draw(screen)
        for e in enemies:   e.draw(screen)
        for p in particles: p.draw(screen)

        draw_ui(screen, score, lives, level)

        pygame.display.flip()
        clock.tick(60)


# ──────────────────────────────────────────
def main():
    start_screen()
    while True:
        score, level = game_loop()
        again = game_over_screen(score, level)
        if not again:
            break
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()