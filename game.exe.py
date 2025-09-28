
import pygame, random, math, webbrowser

pygame.init()

# --------- RESPONSIVE SETTINGS ----------
BASE_WIDTH, BASE_HEIGHT = 800, 600
WIDTH, HEIGHT = 360, 640  # mobile-friendly
SCALE_X = WIDTH / BASE_WIDTH
SCALE_Y = HEIGHT / BASE_HEIGHT
SCALE = min(SCALE_X, SCALE_Y)
GRAVITY = 0.05 * SCALE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Responsive Heart + Fireworks + Button")
clock = pygame.time.Clock()

# ---------------- PARTICLE CLASS ----------------
class Particle:
    def __init__(self, x, y, vx, vy, color, radius=2, life=100, kind="shard"):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.color = color
        self.radius = max(1, int(radius * SCALE))
        self.life = int(life)
        self.kind = kind
        self.exploded = False

    def update(self):
        new_particles = []
        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

        if self.kind == "rocket":
            if self.y < HEIGHT * 0.45 and not self.exploded:
                self.exploded = True
                new_particles = self.explode()
                self.life = 0
            if random.random() < 0.3:
                trail = Particle(
                    self.x, self.y,
                    random.uniform(-0.5, 0.5) * SCALE,
                    random.uniform(0.5, 1.0) * SCALE,
                    (255, 200, 100),
                    radius=2, life=30, kind="trail"
                )
                new_particles.append(trail)
        return new_particles

    def explode(self):
        shards = []
        for i in range(90):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(2, 6) * SCALE
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            color = (
                random.randint(100, 255),
                random.randint(100, 255),
                random.randint(100, 255)
            )
            shards.append(Particle(self.x, self.y, vx, vy, color, radius=2, life=80, kind="shard"))
        return shards

    def draw(self, surf):
        if self.life > 0:
            fade = max(30, int(255 * (self.life / 100)))
            color = (
                min(255, self.color[0] + fade // 4),
                min(255, self.color[1] + fade // 4),
                min(255, self.color[2] + fade // 4)
            )
            pygame.draw.circle(surf, color, (int(self.x), int(self.y)), self.radius)

    def is_dead(self):
        return self.life <= 0 or self.y > HEIGHT + 50

def spawn_rocket(particles):
    x = random.randint(int(WIDTH * 0.15), int(WIDTH * 0.85))
    y = HEIGHT
    vx = random.uniform(-1, 1) * SCALE
    vy = random.uniform(-15, -10) * SCALE
    particles.append(Particle(x, y, vx, vy, (255, 255, 255), radius=3, life=120, kind="rocket"))

# ---------------- HEART SETUP ----------------
def heart_formula(t):
    x = 16 * math.sin(t) ** 3
    y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
    return x, y

heart_points = []
for t in [i * 0.05 for i in range(0, 600)]:
    x, y = heart_formula(t)
    heart_points.append((
        WIDTH // 2 + int(x * 15 * SCALE),
        HEIGHT // 2 - int(y * 15 * SCALE)
    ))

heart_draw_index = 0
heart_lines = []

# ---------------- BUTTON + COUNTDOWN ----------------
portfolio_url = "https://last-page.netlify.app/"
countdown = 10
button_width = int(180 * SCALE)
button_height = int(50 * SCALE)
button_color = (255, 255, 255)
button_hover_color = (200, 200, 200)
button_rect = pygame.Rect(WIDTH - button_width - int(20*SCALE), HEIGHT - button_height - int(20*SCALE), button_width, button_height)
show_button = False
font = pygame.font.SysFont("Arial", max(12,int(28*SCALE)), bold=True)

def draw_button(surface):
    mouse_pos = pygame.mouse.get_pos()
    color = button_hover_color if button_rect.collidepoint(mouse_pos) else button_color
    pygame.draw.rect(surface, color, button_rect, border_radius=3)
    text_surf = font.render("Press Enter", True, (0, 0, 0))
    surface.blit(text_surf, (button_rect.x + button_rect.width//2 - text_surf.get_width()//2,
                             button_rect.y + button_rect.height//2 - text_surf.get_height()//2))

# ---------------- MAIN LOOP ----------------
particles = []
spawn_timer = 0
running = True

while running:
    dt = clock.tick(60)
    screen.fill((10,10,20))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and show_button:
            if button_rect.collidepoint(event.pos):
                webbrowser.open("https://last-page.netlify.app/")
    
    # countdown logic
    if countdown > 0:
        countdown -= dt / 1000  # convert ms to seconds
        countdown_text = font.render(f"{int(countdown)+1}", True, (255,255,255))
        # place above button with small margin
        text_x = button_rect.x + button_rect.width//2 - countdown_text.get_width()//2
        text_y = button_rect.y - countdown_text.get_height() - int(10*SCALE)  # 10 px above button
        screen.blit(countdown_text, (text_x,text_y))
        # screen.blit(countdown_text, (WIDTH//2 - countdown_text.get_width()//2, int(20*SCALE)))
    else:
        show_button = True
        draw_button(screen)
    
    # Fireworks spawn
    spawn_timer += 1
    if spawn_timer > max(6, int(50 * SCALE)):
        spawn_rocket(particles)
        spawn_timer = 0

    # Update particles
    to_add = []
    for p in particles:
        new = p.update()
        if new:
            to_add.extend(new)
    particles.extend(to_add)

    alive = []
    for p in particles:
        p.draw(screen)
        if not p.is_dead():
            alive.append(p)
    particles = alive

    # Draw heart
    step = 2
    if heart_draw_index < len(heart_points):
        i = heart_draw_index
        for j in range(i + step, len(heart_points), step):
            if j - i < 19:
                heart_lines.append((heart_points[i], heart_points[j]))
        heart_draw_index += step

    for line in heart_lines:
        pygame.draw.line(screen, (255, 20, 147), line[0], line[1], max(1, int(1 * SCALE)))

    # Heart text
    if heart_draw_index > len(heart_points) * 0.25:
        texts = [
            "Happy Birthday!",
            "Wishing you a journey of,",
            "luck, love and countless",
            "blessings"
        ]
        for idx, line in enumerate(texts):
            t = font.render(line, True, (255, 0, 0))
            x_pos = WIDTH // 2 - t.get_width() // 2
            y_pos = int(HEIGHT // 2 - 40 * SCALE + idx * (35 * SCALE))
            screen.blit(t, (x_pos, y_pos))

    # Draw button if countdown finished
    if show_button:
        draw_button(screen)

    pygame.display.flip()

pygame.quit()