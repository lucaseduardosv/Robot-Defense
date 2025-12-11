import pygame
import random
import sys 
import math
import os

pygame.init()

LARGURA = 1280
ALTURA = 720
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Robot Defense - Template")
FPS = 60
clock = pygame.time.Clock()

# Duração dos power-ups em ticks (FPS * segundos). Ex.: 60 * 5 = 5s
POWERUP_DURACAO = 60 * 5

BASE = os.path.dirname(__file__)
# Sons
SOM_POWER_UP = pygame.mixer.Sound(os.path.join(BASE, "som", "power up.ogg"))
SOM_EXPLOSAO = pygame.mixer.Sound(os.path.join(BASE, "som", "som-explosão.wav"))
SOM_TIRO = pygame.mixer.Sound(os.path.join(BASE, "som", "Som-laser.wav"))
SOM_DANO = pygame.mixer.Sound(os.path.join(BASE, "som", "som-dano.mp3"))

# Carregar imagem de fundo e ajustar para o tamanho exato da tela (sem rolagem)
img_fundo_orig = pygame.image.load(os.path.join(BASE, "sprites", "background.png")).convert()
FUNDO = pygame.transform.scale(img_fundo_orig, (LARGURA, ALTURA))

# CLASSE BASE
class Entidade(pygame.sprite.Sprite):
    def __init__(self, x, y, velocidade):
        super().__init__()
        self.velocidade = velocidade
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

    def mover(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy


# JOGADOR
class Jogador(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, 7)
        self.image = pygame.image.load(os.path.join(BASE, "sprites", "jogador.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (95, 95))
        self.rect = self.image.get_rect(center=(x, y))
        self.vida = 5

        # Power-ups / estados
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

        # Limitar dentro da tela (usando o tamanho real da imagem para não cortar)
        self.rect.x = max(0, min(self.rect.x, LARGURA - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, ALTURA - self.rect.height))

        # CONTAGEM DOS POWERUPS
        if self.tem_tiro_triplo:
            self.tempo_tiro_triplo -= 1
            if self.tempo_tiro_triplo <= 0:
                self.tem_tiro_triplo = False

        if self.bonus_velocidade > 0:
            self.tempo_velocidade -= 1
            if self.tempo_velocidade <= 0:
                self.bonus_velocidade = 0


# TIRO
class Tiro(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, 10)
        self.image = pygame.Surface((6, 12))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y -= self.velocidade
        if self.rect.y < -10:
            self.kill()


# ROBO BASE
class Robo(Entidade):
    def __init__(self, x, y, velocidade):
        super().__init__(x, y, velocidade)
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


class RoboLento(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=2)  #bem lento
        self.image = pygame.image.load(os.path.join(BASE, "sprites", "robo_lento.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (90, 90))
        self.rect = self.image.get_rect(center=(x, y))
    def atualizar_posicao(self):
        #movimento lento reto para baixo
        self.rect.y += self.velocidade

        #se sair tela, morre igual aos outros
        if self.rect.y > ALTURA:
            self.kill()

class RoboRapido(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=7)
        self.image = pygame.image.load(os.path.join(BASE, "sprites", "RoboRapido.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (80, 80))
        self.jitter = random.choice([-1, 0, 1])

    def atualizar_posicao(self):
        self.rect.y += self.velocidade
        self.rect.x += self.jitter * 2

        if self.rect.x < 0:
            self.rect.x = 0
            self.jitter *= -1
        # Correção do limite direito
        if self.rect.x > LARGURA - self.rect.width:
            self.rect.x = LARGURA - self.rect.width
            self.jitter *= -1


class RoboZigueZague(Robo):
    def __init__(self, x, y, n_pixels=250):
        super().__init__(x, y, velocidade=4)
        self.image = pygame.image.load(os.path.join(BASE, "sprites", "Robozigzag.png")).convert_alpha()
        self.image = pygame.transform.scale_by(self.image, 0.5)     
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direcao = 1
        self.n_pixels = n_pixels
        self.distancia_percorrida = 0

    def atualizar_posicao(self):
        self.rect.y += self.velocidade
        deslocamento = self.direcao * 3
        self.rect.x += deslocamento
        self.distancia_percorrida += abs(deslocamento)

        if self.distancia_percorrida >= self.n_pixels:
            self.direcao *= -1
            self.distancia_percorrida = 0

class RoboSaltador(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=3)
        self.image = pygame.image.load(os.path.join(BASE, "sprites", "robosaltador.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (80, 80))
        self.rect = self.image.get_rect(center=(x, y))

        #comportamentos
        self.salto_forca = random.randint(12, 28)
        self.salto_cooldown = random.randint(30, 90)
        self.salto_timer = 0
        self.dir_x = random.choice([-1, 1])  
        self.vel_x = random.randint(2, 5)   

    def atualizar_posicao(self):
        #movimentos (verticais e horizontais)
        self.rect.y += self.velocidade
        self.rect.x += self.dir_x * self.vel_x
        # Correção limites laterais
        if self.rect.x <= 0 or self.rect.x >= LARGURA - self.rect.width:
            self.dir_x *= -1

        self.salto_timer += 1
        if self.salto_timer >= self.salto_cooldown:
            self.rect.y -= self.salto_forca
            self.salto_timer = 0
            self.salto_cooldown = random.randint(30, 90)
        if self.rect.y > ALTURA:
            self.kill()


class RoboCiclico(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade = 3)
        self.image = pygame.image.load(os.path.join(BASE, "sprites", "RoboCiclico.png")).convert_alpha()
        self.raio = 60
        self.angulo = 0
        self.velang = 4.0

        self.centrox = float(x)
        self.centroy = float(y)
       
        self.rect = self.image.get_rect(center=(x,y))

    def atualizar_posicao(self):
        self.centroy += self.velocidade
        self.angulo += self.velang

        angulo_rad = math.radians(self.angulo)
        novo_x = self.centrox + self.raio * math.cos(angulo_rad)
        novo_y = self.centroy + self.raio * math.sin(angulo_rad)
        self.rect.x = int(novo_x)
        self.rect.y = int(novo_y)
        self.rect.x = max(0, min(self.rect.x, LARGURA - self.rect.width ))


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
            pygame.draw.circle(surf, (255, 80, 0, 150), (radius, radius), max(1, radius // 2))
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

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, cor):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(cor)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = 3

    def update(self):
        self.rect.y += self.vel
        if self.rect.y > ALTURA + 20:
            self.kill()


class PU_VidaExtra(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, (0, 150, 255))


class PU_Velocidade(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, (255, 255, 0))


class PU_TiroTriplo(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, (255, 100, 0))



def start_game_fire():
    # Garante a resolução correta ao iniciar o jogo
    global TELA
    TELA = pygame.display.set_mode((LARGURA, ALTURA))

    #GRUPOS
    todos_sprites = pygame.sprite.Group()
    
    def criar_tiro(x, y, jogador_ref):
        t = Tiro(x, y)
        todos_sprites.add(t)
        tiros.add(t)
        SOM_TIRO.play()
        
    inimigos = pygame.sprite.Group()
    tiros = pygame.sprite.Group()
    explosoes = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    jogador = Jogador(LARGURA // 2, ALTURA - 100)
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
                if event.key == pygame.K_ESCAPE:
                    rodando = False

                if event.key == pygame.K_SPACE:
                    if jogador.tem_tiro_triplo:
                        criar_tiro(jogador.rect.centerx, jogador.rect.y, jogador)
                        criar_tiro(jogador.rect.centerx - 18, jogador.rect.y, jogador)
                        criar_tiro(jogador.rect.centerx + 18, jogador.rect.y, jogador)
                    else:
                        criar_tiro(jogador.rect.centerx, jogador.rect.y, jogador)

        timer_tiro += 1
        if pygame.mouse.get_pressed()[0] and timer_tiro >= 10:
            if jogador.tem_tiro_triplo:
                criar_tiro(jogador.rect.centerx, jogador.rect.y, jogador)
                criar_tiro(jogador.rect.centerx - 18, jogador.rect.y, jogador)
                criar_tiro(jogador.rect.centerx + 18, jogador.rect.y, jogador)
            else:
                criar_tiro(jogador.rect.centerx, jogador.rect.y, jogador)
            timer_tiro = 0

        spawn_timer += 1
        if spawn_timer > 40:
            tipo = random.choice(["zig", "rapido", "saltar", "ciclico", "lento"])
            # Ajustei o spawn para garantir que nasçam dentro da tela larga
            start_x = random.randint(50, LARGURA - 100)
            
            if tipo == "zig":
                robo = RoboZigueZague(start_x, -40)
            elif tipo == "rapido":
                robo = RoboRapido(start_x, -40)
            elif tipo == "saltar":
                robo = RoboSaltador(start_x, -40)
            elif tipo == "ciclico":
                robo = RoboCiclico(start_x, -40)
            elif tipo == "lento":
                robo = RoboLento(start_x, -40)

            todos_sprites.add(robo)
            inimigos.add(robo)
            spawn_timer = 0

        if random.random() < 0.01:
            tipo_p = random.choice(["vida", "vel", "triplo"])
            x = random.randint(50, LARGURA - 100)
            if tipo_p == "vida":
                p = PU_VidaExtra(x, -30)
            elif tipo_p == "vel":
                p = PU_Velocidade(x, -30)
            else:
                p = PU_TiroTriplo(x, -30)
            todos_sprites.add(p)
            powerups.add(p)

        colisoes = pygame.sprite.groupcollide(inimigos, tiros, False, True)
        for robo, lista_tiros in colisoes.items():
            if robo.explodindo:
                continue

            robo.start_explosion()
            SOM_EXPLOSAO.play()

            explosao = Explosion(robo.rect.center, target_enemy=robo)
            todos_sprites.add(explosao)
            explosoes.add(explosao)

            pontos += 1
        
        if pygame.sprite.spritecollide(jogador, inimigos, True):
            SOM_DANO.play()
            jogador.vida -= 1
            if jogador.vida <= 0:
                print("GAME OVER!")
                rodando = False

        pegou = pygame.sprite.spritecollide(jogador, powerups, True)
        for p in pegou:
            SOM_POWER_UP.play()

            if isinstance(p, PU_VidaExtra):
                jogador.vida += 1
            elif isinstance(p, PU_Velocidade):
                jogador.bonus_velocidade = 3
                jogador.tempo_velocidade = POWERUP_DURACAO
            elif isinstance(p, PU_TiroTriplo):
                jogador.tem_tiro_triplo = True
                jogador.tempo_tiro_triplo = POWERUP_DURACAO

        todos_sprites.update()

        # Desenhar fundo FIXO (preenchendo tudo)
        TELA.blit(FUNDO, (0, 0))

        todos_sprites.draw(TELA)

        font = pygame.font.SysFont(None, 30)
        texto = font.render(f"Vida: {jogador.vida}  |  Pontos: {pontos}", True, (255, 255, 255))
        TELA.blit(texto, (10, 10))

        y_offset = 40
        if jogador.bonus_velocidade > 0:
            segundos = max(0, jogador.tempo_velocidade // FPS)
            TELA.blit(font.render(f"Velocidade: {segundos}s", True, (255, 255, 255)), (10, y_offset))
            y_offset += 22
        if jogador.tem_tiro_triplo:
            segundos = max(0, jogador.tempo_tiro_triplo // FPS)
            TELA.blit(font.render(f"Tiro Triplo: {segundos}s", True, (255, 255, 255)), (10, y_offset))

        pygame.display.flip()

    # pygame.quit()