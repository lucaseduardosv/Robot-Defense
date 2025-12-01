import pygame
import random

pygame.init()

LARGURA = 800
ALTURA = 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Robot Defense - Template")
FPS = 60
clock = pygame.time.Clock()


# CLASSE BASE
class Entidade(pygame.sprite.Sprite):
    def __init__(self, x, y, velocidade):
        super().__init__()
        self.velocidade = velocidade
        self.image = pygame.Surface((40, 40))
        self.rect = self.image.get_rect(center=(x, y))

    def mover(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy


# JOGADOR
class Jogador(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, 5)
        self.image.fill((0, 255, 0))  # verde
        self.vida = 5

    def update(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.mover(0, -self.velocidade)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.mover(0, self.velocidade)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.mover(-self.velocidade, 0)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.mover(self.velocidade, 0)

        self.rect.x = max(0, min(self.rect.x, LARGURA - 40))
        self.rect.y = max(0, min(self.rect.y, ALTURA - 40))


# TIRO
class Tiro(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, 10)
        self.image.fill((255, 255, 0))

    def update(self):
        self.rect.y -= self.velocidade
        if self.rect.y < 0:
            self.kill()


# ROBO BASE
class Robo(Entidade):
    def __init__(self, x, y, velocidade):
        super().__init__(x, y, velocidade)
        self.image.fill((255, 0, 0))
        self.explodindo = False
        self.explosion_done = False

    def start_explosion(self):
        if self.explodindo:
            return
        self.explodindo = True

    def update(self):
        if not self.explodindo:
            self.atualizar_posicao()
            if self.rect.y > ALTURA:
                self.kill()
        else:
            if self.explosion_done:
                self.kill()

    def atualizar_posicao(self):
        raise NotImplementedError


class RoboRapido(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=6)
        self.jitter = random.choice([-1, 0, 1])

    def atualizar_posicao(self):
        self.rect.y += self.velocidade
        self.rect.x += self.jitter * 2

        if self.rect.x < 0:
            self.rect.x = 0
            self.jitter *= -1
        if self.rect.x > LARGURA - 40:
            self.rect.x = LARGURA - 40
            self.jitter *= -1


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, target_enemy=None, max_radius=50, frames=8):
        super().__init__()
        self.target_enemy = target_enemy
        self.frames = []
        self.frame_index = 0

        for i in range(1, frames + 1):
            radius = int(max_radius * (i / frames))
            surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 150, 0, 200), (radius, radius), radius)
            pygame.draw.circle(surf, (255, 80, 0, 150), (radius, radius), radius // 2)
            self.frames.append(surf)

        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=center)
        self.ticks = 0

    def update(self):
        self.ticks += 1
        if self.ticks % 4 == 0:
            self.frame_index += 1

            if self.frame_index >= len(self.frames):
                if self.target_enemy:
                    self.target_enemy.explosion_done = True
                self.kill()
                return

            center = self.rect.center
            self.image = self.frames[self.frame_index]
            self.rect = self.image.get_rect(center=center)


# ROBO ZIGUE-ZAGUE
class RoboZigueZague(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=3)
        self.direcao = 1

    def atualizar_posicao(self):
        self.rect.y += self.velocidade
        self.rect.x += self.direcao * 3

        if self.rect.x <= 0 or self.rect.x >= LARGURA - 40:
            self.direcao *= -1


todos_sprites = pygame.sprite.Group()
inimigos = pygame.sprite.Group()
tiros = pygame.sprite.Group()
explosoes = pygame.sprite.Group()

jogador = Jogador(LARGURA // 2, ALTURA - 60)
todos_sprites.add(jogador)

pontos = 0
spawn_timer = 0
timer_tiro = 0

rodando = True
while rodando:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                tiro = Tiro(jogador.rect.centerx, jogador.rect.y)
                todos_sprites.add(tiro)
                tiros.add(tiro)

    timer_tiro += 1
    mouse_click = pygame.mouse.get_pressed()

    if mouse_click[0] and timer_tiro >= 10:
        tiro = Tiro(jogador.rect.centerx, jogador.rect.y)
        todos_sprites.add(tiro)
        tiros.add(tiro)
        timer_tiro = 0

    spawn_timer += 1
    if spawn_timer > 40:
        robo = RoboZigueZague(random.randint(40, LARGURA - 40), -40)
        todos_sprites.add(robo)
        inimigos.add(robo)
        spawn_timer = 0

    colisoes = pygame.sprite.groupcollide(inimigos, tiros, False, True)

    for robo, lista_tiros in colisoes.items():
        if robo.explodindo:
            continue

        robo.start_explosion()

        explosao = Explosion(robo.rect.center, target_enemy=robo)
        todos_sprites.add(explosao)
        explosoes.add(explosao)

    if pygame.sprite.spritecollide(jogador, inimigos, True):
        jogador.vida -= 1
        if jogador.vida <= 0:
            print("GAME OVER!")
            rodando = False

    todos_sprites.update()

    TELA.fill((20, 20, 20))
    todos_sprites.draw(TELA)

    font = pygame.font.SysFont(None, 30)
    texto = font.render(f"Vida: {jogador.vida}  |  Pontos: {pontos}", True, (255, 255, 255))
    TELA.blit(texto, (10, 10))

    pygame.display.flip()

pygame.quit()
