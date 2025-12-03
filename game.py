import pygame
import random
import os

pygame.init()

LARGURA = 800
ALTURA = 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Robot Defense - Template")
FPS = 60
clock = pygame.time.Clock()

# caminho da base
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

#fundo do jogo
path_fundo = os.path.join(BASE_PATH, "fundo.png")
if os.path.exists(path_fundo):
    fundo_jogo = pygame.image.load(path_fundo).convert()
    fundo = pygame.transform.scale(fundo_jogo, (LARGURA, 
else:
    fundo = pygame.Surface((LARGURA, ALTURA))
    fundo.fill((15, 15, 15))

#Duração dos power-ups em ticks (FPS * segundos). Ex.: 60
POWERUP_DURACAO = 5 * 60  

# classe base
class Entidade(pygame.sprite.Sprite):
    def __init__(self, x, y, velocidade):
        super().__init__()
        self.velocidade = velocidade
        self.image = pygame.Surface((40, 40), pygame.SRCA
        self.rect = self.image.get_rect(center=(x, y))

    def mover(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

# classe jogador
class Jogador(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, 5)
        self.image.fill((0, 200, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.vida = 5

        self.bonus_velocidade = 0
        self.tem_tiro_triplo = False
        self.tempo_tiro_triplo = 0
        self.tempo_velocidade = 0

    def update(self):
        keys = pygame.key.get_pressed()
        vel = self.velocidade + self.bonus_velocidade

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.mover(0, -vel)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.mover(0, vel)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.mover(-vel, 0)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.mover(vel, 0)

        self.rect.x = max(0, min(self.rect.x, LARGURA - s
        self.rect.y = max(0, min(self.rect.y, ALTURA - se

        if self.tem_tiro_triplo:
            self.tempo_tiro_triplo -= 1
            if self.tempo_tiro_triplo <= 0:
                self.tem_tiro_triplo = False

        if self.bonus_velocidade > 0:
            self.tempo_velocidade -= 1
            if self.tempo_velocidade <= 0:
                self.bonus_velocidade = 0

# class tiro
class Tiro(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, 10)
        self.image = pygame.Surface((6, 12), pygame.SRCAL
        pygame.draw.rect(self.image, (255, 255, 0), (0, 0
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y -= self.velocidade
        if self.rect.y < -10:
            self.kill()

# class robo
class Robo(Entidade):
    def __init__(self, x, y, velocidade):
        super().__init__(x, y, velocidade)
        # Removido o fill vermelho aqui para não sobrescr
        # self.image.fill((255, 0, 0))
        self.explodindo = False
        self.explosion_done = False

    def start_explosion(self):
        if not self.explodindo:
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

# classe robo rapido
class RoboRapido(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, 6)
        self.image.fill((255, 0, 0))
        self.jitter = random.choice([-2, -1, 0, 1, 2])

    def atualizar_posicao(self):
        self.rect.y += self.velocidade
        self.rect.x += self.jitter

#roboziguezague
class RoboZigueZague(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, 3)
        self.image.fill((200, 30, 30))
        self.direcao = 1

    def atualizar_posicao(self):
        self.rect.y += self.velocidade
        self.rect.x += self.direcao * 3

        if self.rect.x <= 0 or self.rect.x >= LARGURA - s
            self.direcao *= -1

#classe saltador
class RoboSaltador(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, 2)

        path = os.path.join(BASE_PATH, "sprites", "robosa
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (40, 40))
            self.image = img
        else:
            self.image.fill((180, 50, 180))

        self.rect = self.image.get_rect(center=(x, y))

        self.salto_forca = random.randint(12, 28)
        self.salto_cooldown = random.randint(30, 90)
        self.salto_timer = 0
        self.dir_x = random.choice([-1, 1])
        self.vel_x = random.randint(2, 4)

    def atualizar_posicao(self):
        #movimentos (verticais e horizontais)
        self.rect.y += self.velocidade
        self.rect.x += self.dir_x * self.vel_x

        if self.rect.x <= 0 or self.rect.x >= LARGURA - s
            self.dir_x *= -1

        self.salto_timer += 1
        if self.salto_timer >= self.salto_cooldown:
            self.rect.y -= self.salto_forca
            self.salto_timer = 0
            self.salto_cooldown = random.randint(30, 90)


# o robo lento
class RoboLento(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, 1.5)

        path = os.path.join(BASE_PATH, "sprites", "robo_l

        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (40, 40))
            self.image = img
        else:
            print("⚠ Arquivo sprites/robo_lento.png não 
            self.image.fill((100, 200, 100))

        self.rect = self.image.get_rect(center=(x, y))

    def atualizar_posicao(self):
        self.rect.y += self.velocidade

# class explosion
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, target_enemy=None):
        super().__init__()
        self.target_enemy = target_enemy
        self.frames = []
        self.frame_index = 0

        for i in range(1, 9):
            radius = i * 6
            surf = pygame.Surface((radius * 2, radius * 2
            pygame.draw.circle(surf, (255, 150, 0, 200), 
            pygame.draw.circle(surf, (255, 80, 0, 150), (
            self.frames.append(surf)

        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=center)

    def update(self):
        self.frame_index += 1
        if self.frame_index >= len(self.frames):
            if self.target_enemy:
                self.target_enemy.explosion_done = True
            self.kill()
            return

        center = self.rect.center
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=center)

# PowerUp
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, cor):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(cor)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = 2

    def update(self):
        self.rect.y += self.vel
        if self.rect.y > ALTURA:
            self.kill()


class PU_VidaExtra(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, (0, 150, 255))


class PU_Velocidade(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, (255, 255, 0))


class PU_TiroTriplo(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, (255, 120, 0))

# grupos
todos_sprites = pygame.sprite.Group()
inimigos = pygame.sprite.Group()
tiros = pygame.sprite.Group()
explosoes = pygame.sprite.Group()
powerups = pygame.sprite.Group()

jogador = Jogador(LARGURA // 2, ALTURA - 60)
todos_sprites.add(jogador)

spawn_timer = 0
pontos = 0
timer_tiro = 0


def criar_tiro(x, y):
    t = Tiro(x, y)
    todos_sprites.add(t)
    tiros.add(t)

# funcao main
def main():
    global spawn_timer, pontos, timer_tiro
    rodando = True
    spawn_timer = 0
    pontos = 0

    while rodando:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # tiro triplo
                    if jogador.tem_tiro_triplo:
                        criar_tiro(jogador.rect.centerx -
                        criar_tiro(jogador.rect.centerx, 
                        criar_tiro(jogador.rect.centerx +
                    else:
                        criar_tiro(jogador.rect.centerx, 

        # tiro com mouse
        timer_tiro += 1
        if pygame.mouse.get_pressed()[0] and timer_tiro >
            if jogador.tem_tiro_triplo:
                criar_tiro(jogador.rect.centerx - 18, jog
                criar_tiro(jogador.rect.centerx, jogador.
                criar_tiro(jogador.rect.centerx + 18, jog
            else:
                criar_tiro(jogador.rect.centerx, jogador.
            timer_tiro = 0

# spawn de robos
        spawn_timer += 1
        if spawn_timer > 40:
            tipos = ["rapido", "zig", "saltar", "lento"]
            escolha = random.choice(tipos)
            x = random.randint(40, LARGURA - 40)

            if escolha == "rapido":
                r = RoboRapido(x, -40)
            elif escolha == "zig":
                r = RoboZigueZague(x, -40)
            elif escolha == "saltar":
                r = RoboSaltador(x, -40)
            else:
                r = RoboLento(x, -40)

            inimigos.add(r)
            todos_sprites.add(r)
            spawn_timer = 0

# powerups
        if random.random() < 0.01:
            x = random.randint(40, LARGURA - 40)
            tipo = random.choice(["vida", "vel", "triplo"

            if tipo == "vida":
                p = PU_VidaExtra(x, -30)
            elif tipo == "vel":
                p = PU_Velocidade(x, -30)
            else:
                p = PU_TiroTriplo(x, -30)

            powerups.add(p)
            todos_sprites.add(p)

        # tiros robo colisoes
        hits = pygame.sprite.groupcollide(inimigos, tiros
        for robo, lista in hits.items():
            robo.start_explosion()
            expl = Explosion(robo.rect.center, target_ene
            todos_sprites.add(expl)
            explosoes.add(expl)
            pontos += 1

        # jogador atingido
        if pygame.sprite.spritecollide(jogador, inimigos,
            jogador.vida -= 1
            if jogador.vida <= 0:
                print("GAME OVER!")
                rodando = False

        # pegando powerup
        pegos = pygame.sprite.spritecollide(jogador, powe
        for p in pegos:
            if isinstance(p, PU_VidaExtra):
                jogador.vida += 1
            elif isinstance(p, PU_Velocidade):
                jogador.bonus_velocidade = 3
                jogador.tempo_velocidade = POWERUP_DURACA
            elif isinstance(p, PU_TiroTriplo):
                jogador.tem_tiro_triplo = True
                jogador.tempo_tiro_triplo = POWERUP_DURAC

        todos_sprites.update()

        # fundo
        TELA.blit(fundo, (0, 0))

        todos_sprites.draw(TELA)

        # HUD
        font = pygame.font.SysFont(None, 28)
        texto = font.render(f"Vida: {jogador.vida}  |  Po
        TELA.blit(texto, (10, 10))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
