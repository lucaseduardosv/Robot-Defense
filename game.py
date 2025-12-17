import pygame
import random
import sys
import math
import os

pygame.init()

LARGURA = 1280
ALTURA = 720
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Robot Defense")
FPS = 60
clock = pygame.time.Clock()

POWERUP_DURACAO = 60 * 5
PONTOS_PARA_BOSS = 30

BASE = os.path.dirname(__file__)

def carregar_som(nome):
    path = os.path.join(BASE, "som", nome)
    try:
        return pygame.mixer.Sound(path)
    except:
        return pygame.mixer.Sound(buffer=bytearray([0]*100))

SOM_POWER_UP = carregar_som("power up.ogg")
SOM_EXPLOSAO = carregar_som("som-explosão.wav")
SOM_TIRO = carregar_som("Som-laser.wav")
SOM_DANO = carregar_som("som-dano.mp3")

try:
    img_fundo_orig = pygame.image.load(os.path.join(BASE, "sprites", "background.png")).convert()
    FUNDO = pygame.transform.scale(img_fundo_orig, (LARGURA, ALTURA))
except:
    FUNDO = pygame.Surface((LARGURA, ALTURA))
    FUNDO.fill((30, 30, 30))

class Entidade(pygame.sprite.Sprite):
    def __init__(self, x, y, velocidade):
        super().__init__()
        self.velocidade = velocidade
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

    def mover(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

class Jogador(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, 7)
        try:
            self.image = pygame.image.load(os.path.join(BASE, "sprites", "jogador.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (95, 95))
        except:
            self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.vida = 5
        self.bonus_velocidade = 0
        self.tem_tiro_triplo = False
        self.tempo_tiro_triplo = 0
        self.tempo_velocidade = 0

    def update(self):
        keys = pygame.key.get_pressed()
        vel = self.velocidade + self.bonus_velocidade

        if keys[pygame.K_w] or keys[pygame.K_UP]: self.mover(0, -vel)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: self.mover(0, vel)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.mover(-vel, 0)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.mover(vel, 0)

        self.rect.x = max(0, min(self.rect.x, LARGURA - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, ALTURA - self.rect.height))

        if self.tem_tiro_triplo:
            self.tempo_tiro_triplo -= 1
            if self.tempo_tiro_triplo <= 0: self.tem_tiro_triplo = False
        if self.bonus_velocidade > 0:
            self.tempo_velocidade -= 1
            if self.tempo_velocidade <= 0: self.bonus_velocidade = 0

class Tiro(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, 10)
        self.image = pygame.Surface((6, 12))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
    def update(self):
        self.rect.y -= self.velocidade
        if self.rect.y < -10: self.kill()

class TiroInimigo(Entidade):
    def __init__(self, x, y, angle=90, speed=8):
        super().__init__(x, y, speed)
        self.image = pygame.Surface((8, 16))
        self.image.fill((255, 50, 50))
        self.rect = self.image.get_rect(center=(x, y))
        self.angle_rad = math.radians(angle)
    def update(self):
        self.rect.x += math.cos(self.angle_rad) * self.velocidade
        self.rect.y += math.sin(self.angle_rad) * self.velocidade
        if self.rect.y > ALTURA + 50 or self.rect.y < -50 or self.rect.x < -50 or self.rect.x > LARGURA + 50:
            self.kill()

class Robo(Entidade):
    def __init__(self, x, y, velocidade):
        super().__init__(x, y, velocidade)
        self.explodindo = False
        self.explosion_done = False
    def start_explosion(self):
        if self.explodindo: return
        self.explodindo = True
    def update(self):
        if not self.explodindo:
            self.atualizar_posicao()
            if self.rect.y > ALTURA: self.kill()
        else:
            if self.explosion_done: self.kill()
    def atualizar_posicao(self):
        raise NotImplementedError

class RoboLento(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=2)
        try:
            self.image = pygame.image.load(os.path.join(BASE, "sprites", "robo_lento.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (90, 90))
        except: self.image.fill((100,100,100))
        self.rect = self.image.get_rect(center=(x, y))
    def atualizar_posicao(self):
        self.rect.y += self.velocidade

class RoboRapido(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=5)
        try:
            self.image = pygame.image.load(os.path.join(BASE, "sprites", "RoboRapido.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (80, 80))
        except: self.image.fill((200,50,50))
        self.rect = self.image.get_rect(center=(x,y))
        self.jitter = random.choice([-1, 0, 1])
    def atualizar_posicao(self):
        self.rect.y += self.velocidade
        self.rect.x += self.jitter * 2
        if self.rect.x < 0 or self.rect.x > LARGURA - self.rect.width:
            self.jitter *= -1

class RoboZigueZague(Robo):
    def __init__(self, x, y, n_pixels=250):
        super().__init__(x, y, velocidade=3)
        try:
            self.image = pygame.image.load(os.path.join(BASE, "sprites", "Robozigzag.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (70, 70))
        except: self.image.fill((50,200,50))
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
        try:
            self.image = pygame.image.load(os.path.join(BASE, "sprites", "robosaltador.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (80, 80))
        except: self.image.fill((50,50,200))
        self.rect = self.image.get_rect(center=(x, y))
        self.salto_forca = random.randint(12, 28)
        self.salto_cooldown = random.randint(30, 90)
        self.salto_timer = 0
        self.dir_x = random.choice([-1, 1])
        self.vel_x = random.randint(2, 5)
    def atualizar_posicao(self):
        self.rect.y += self.velocidade
        self.rect.x += self.dir_x * self.vel_x
        if self.rect.x <= 0 or self.rect.x >= LARGURA - self.rect.width: self.dir_x *= -1
        self.salto_timer += 1
        if self.salto_timer >= self.salto_cooldown:
            self.rect.y -= self.salto_forca
            self.salto_timer = 0
            self.salto_cooldown = random.randint(30, 90)

class RoboCiclico(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=3)
        try:
            self.image = pygame.image.load(os.path.join(BASE, "sprites", "RoboCiclico.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (60, 60))
        except: 
            self.image = pygame.Surface((60, 60))
            self.image.fill((255,0,255))
        self.raio = 60
        self.angulo = 0
        self.velang = 4.0
        self.centrox = float(x)
        self.centroy = float(y)
        self.rect = self.image.get_rect(center=(x,y))
    def atualizar_posicao(self):
        self.centroy += self.velocidade
        self.angulo += self.velang
        rad = math.radians(self.angulo)
        self.rect.x = int(self.centrox + self.raio * math.cos(rad))
        self.rect.y = int(self.centroy + self.raio * math.sin(rad))

class RoboChefao(Entidade):
    def __init__(self, x, y, jogador_alvo):
        super().__init__(x, y, velocidade=4)
        self.jogador_alvo = jogador_alvo
        try:
            self.image_original = pygame.image.load(os.path.join(BASE, "sprites", "boss2.png")).convert_alpha()
        except:
            self.image_original = pygame.Surface((200, 200))
            self.image_original.fill((100, 0, 100))
        
        self.image_original = pygame.transform.scale(self.image_original, (250, 250))
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect(center=(x, y))

        self.vida_max = 200
        self.vida = self.vida_max
        self.furia_ativa = False
        
        self.estado = 'entrada'
        self.destino_y = 150
        
        self.timer_tiro = 0
        self.cooldown_tiro = 60
        self.timer_dash = 0
        self.cooldown_dash = 240
        
        self.dir_move = 1
        self.dash_vector = pygame.math.Vector2(0, 0)

    def update(self):
        if self.vida <= self.vida_max / 2 and not self.furia_ativa:
            self.furia_ativa = True
            self.cooldown_tiro = 25
            self.velocidade = 7
            self.cooldown_dash = 150
            vermelho = pygame.Surface(self.image_original.get_size()).convert_alpha()
            vermelho.fill((255, 50, 50, 100))
            self.image = self.image_original.copy()
            self.image.blit(vermelho, (0,0), special_flags=pygame.BLEND_MULT)

        if self.estado == 'entrada':
            if self.rect.centery < self.destino_y:
                self.rect.y += 2
            else:
                self.estado = 'movendo'

        elif self.estado == 'movendo':
            self.rect.x += self.velocidade * self.dir_move
            if self.rect.right >= LARGURA - 20: self.dir_move = -1
            if self.rect.left <= 20: self.dir_move = 1
            
            self.timer_dash += 1
            if self.timer_dash >= self.cooldown_dash:
                self.estado = 'preparando_dash'
                self.timer_dash = 0
            
            self.timer_tiro += 1
            if self.timer_tiro >= self.cooldown_tiro:
                self.timer_tiro = 0

        elif self.estado == 'preparando_dash':
            jitter_x = random.randint(-5, 5)
            self.rect.x += jitter_x
            self.timer_dash += 1
            if self.timer_dash > 40:
                self.estado = 'dashing'
                if self.jogador_alvo and self.jogador_alvo.alive():
                    px, py = self.jogador_alvo.rect.center
                else:
                    px, py = LARGURA//2, ALTURA

                start = pygame.math.Vector2(self.rect.center)
                end = pygame.math.Vector2(px, py)
                direction = end - start
                if direction.length() > 0:
                    direction = direction.normalize()
                speed_dash = 25 if self.furia_ativa else 18
                self.dash_vector = direction * speed_dash

        elif self.estado == 'dashing':
            self.rect.x += self.dash_vector.x
            self.rect.y += self.dash_vector.y
            
            if (self.rect.top > ALTURA) or (self.rect.bottom < 0) or \
               (self.rect.left > LARGURA) or (self.rect.right < 0):
                self.rect.centerx = LARGURA // 2
                self.rect.bottom = 0
                self.estado = 'entrada'

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
                if self.target_enemy: self.target_enemy.explosion_done = True
                self.kill()
                return
            self.image = self.frames[self.frame_index]
            self.rect = self.image.get_rect(center=self.rect.center)

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, cor):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(cor)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = 3
    def update(self):
        self.rect.y += self.vel
        if self.rect.y > ALTURA + 20: self.kill()

class PU_VidaExtra(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, (0, 150, 255))
        try:
            self.image = pygame.image.load(os.path.join(BASE, "sprites", "power_up_vida.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (30, 30))
        except: pass
class PU_Velocidade(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, (255, 255, 0))
        try:
            self.image = pygame.image.load(os.path.join(BASE, "sprites", "power_up_velocidade.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (30, 30))
        except: pass
class PU_TiroTriplo(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, (255, 100, 0))
        try:
            self.image = pygame.image.load(os.path.join(BASE, "sprites", "power_up_tiro_triplo.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (30, 30))
        except: pass

def start_game_fire():
    global TELA
    pygame.font.init()
    fonte_hud = pygame.font.SysFont("Arial", 25, bold=True)
    
    TELA = pygame.display.set_mode((LARGURA, ALTURA))

    todos_sprites = pygame.sprite.Group()
    inimigos = pygame.sprite.Group()
    tiros_jogador = pygame.sprite.Group()
    tiros_inimigo = pygame.sprite.Group()
    explosoes = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    boss_group = pygame.sprite.GroupSingle()

    jogador = Jogador(LARGURA // 2, ALTURA - 100)
    todos_sprites.add(jogador)

    def criar_tiro(x, y):
        t = Tiro(x, y)
        todos_sprites.add(t)
        tiros_jogador.add(t)
        SOM_TIRO.play()

    pontos = 0
    spawn_timer = 0
    timer_tiro_mouse = 0
    boss_ativo = False
    intervalo_spawn = 45

    rodando = True
    while rodando:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: rodando = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: rodando = False
                if event.key == pygame.K_SPACE:
                    if jogador.tem_tiro_triplo:
                        criar_tiro(jogador.rect.centerx, jogador.rect.y)
                        criar_tiro(jogador.rect.centerx - 18, jogador.rect.y)
                        criar_tiro(jogador.rect.centerx + 18, jogador.rect.y)
                    else:
                        criar_tiro(jogador.rect.centerx, jogador.rect.y)

        timer_tiro_mouse += 1
        if pygame.mouse.get_pressed()[0] and timer_tiro_mouse >= 10:
            if jogador.tem_tiro_triplo:
                criar_tiro(jogador.rect.centerx, jogador.rect.y)
                criar_tiro(jogador.rect.centerx - 18, jogador.rect.y)
                criar_tiro(jogador.rect.centerx + 18, jogador.rect.y)
            else:
                criar_tiro(jogador.rect.centerx, jogador.rect.y)
            timer_tiro_mouse = 0

        if not boss_ativo:
            spawn_timer += 1
            if pontos >= PONTOS_PARA_BOSS:
                boss_ativo = True
                for inimigo in inimigos:
                    inimigo.kill()
                    explosao = Explosion(inimigo.rect.center)
                    todos_sprites.add(explosao)
                
                o_boss = RoboChefao(LARGURA//2, -200, jogador)
                boss_group.add(o_boss)
                todos_sprites.add(o_boss)
            
            elif spawn_timer > intervalo_spawn:
                tipo = random.choice(["zig", "rapido", "saltar", "ciclico", "lento"])
                start_x = random.randint(50, LARGURA - 100)
                
                if tipo == "zig": r = RoboZigueZague(start_x, -40)
                elif tipo == "rapido": r = RoboRapido(start_x, -40)
                elif tipo == "saltar": r = RoboSaltador(start_x, -40)
                elif tipo == "ciclico": r = RoboCiclico(start_x, -40)
                else: r = RoboLento(start_x, -40)
                
                todos_sprites.add(r)
                inimigos.add(r)
                spawn_timer = 0
                intervalo_spawn = max(15, 45 - (pontos // 5))

        if boss_ativo and boss_group:
            boss = boss_group.sprite
            if boss.estado == 'movendo' and boss.timer_tiro == 0:
                angles = [70, 80, 90, 100, 110] if boss.furia_ativa else [80, 90, 100]
                spd = 11 if boss.furia_ativa else 8
                for ang in angles:
                    tb = TiroInimigo(boss.rect.centerx, boss.rect.bottom, angle=ang, speed=spd)
                    todos_sprites.add(tb)
                    tiros_inimigo.add(tb)

        if random.random() < 0.003:
            tipo_p = random.choice(["vida", "vel", "triplo"])
            x = random.randint(50, LARGURA - 100)
            if tipo_p == "vida": p = PU_VidaExtra(x, -30)
            elif tipo_p == "vel": p = PU_Velocidade(x, -30)
            else: p = PU_TiroTriplo(x, -30)
            todos_sprites.add(p)
            powerups.add(p)

        hits_powerup = pygame.sprite.spritecollide(jogador, powerups, True)
        for p in hits_powerup:
            SOM_POWER_UP.play()
            if isinstance(p, PU_VidaExtra):
                jogador.vida += 1
            elif isinstance(p, PU_Velocidade):
                jogador.bonus_velocidade = 5
                jogador.tempo_velocidade = 400
            elif isinstance(p, PU_TiroTriplo):
                jogador.tem_tiro_triplo = True
                jogador.tempo_tiro_triplo = 400

        colisoes = pygame.sprite.groupcollide(inimigos, tiros_jogador, False, True)
        for robo, lista_tiros in colisoes.items():
            if robo.explodindo: continue
            robo.start_explosion()
            SOM_EXPLOSAO.play()
            explosao = Explosion(robo.rect.center, target_enemy=robo)
            todos_sprites.add(explosao)
            explosoes.add(explosao)
            pontos += 1
        
        if boss_ativo:
            boss = boss_group.sprite
            hits = pygame.sprite.spritecollide(boss, tiros_jogador, True)
            for hit in hits:
                boss.vida -= 1
                SOM_DANO.play()
                if boss.vida <= 0:
                    SOM_EXPLOSAO.play()
                    for _ in range(8):
                        offset_x = random.randint(-60, 60)
                        offset_y = random.randint(-60, 60)
                        ex = Explosion((boss.rect.centerx + offset_x, boss.rect.centery + offset_y))
                        todos_sprites.add(ex)
                    boss.kill()
                    boss_ativo = False
                    pontos += 100

        hits_player_tiro = pygame.sprite.spritecollide(jogador, tiros_inimigo, True)
        hits_player_corpo = pygame.sprite.spritecollide(jogador, inimigos, True)
        dano_total = len(hits_player_tiro) + len(hits_player_corpo)
        
        if boss_ativo and boss_group:
            if pygame.sprite.collide_rect(jogador, boss_group.sprite):
                 dano_total += 1
                 if jogador.rect.x < boss_group.sprite.rect.x: jogador.rect.x -= 30
                 else: jogador.rect.x += 30

        if dano_total > 0:
            SOM_DANO.play()
            jogador.vida -= 1
            if jogador.vida <= 0:
                print(f"Game Over! Pontos: {pontos}")
                rodando = False

        todos_sprites.update()
        TELA.blit(FUNDO, (0, 0))
        todos_sprites.draw(TELA)
        
        texto_pontos = fonte_hud.render(f"PONTOS: {pontos}", True, (255, 255, 255))
        texto_vida = fonte_hud.render(f"VIDA: {jogador.vida}", True, (255, 50, 50))
        sombra_pontos = fonte_hud.render(f"PONTOS: {pontos}", True, (0, 0, 0))
        
        TELA.blit(sombra_pontos, (22, 22))
        TELA.blit(texto_pontos, (20, 20))
        TELA.blit(texto_vida, (20, 50))

        if boss_ativo and boss_group:
            boss = boss_group.sprite
            largura_barra = 400
            altura_barra = 20
            pos_x_barra = (LARGURA - largura_barra) // 2
            pos_y_barra = 20
            pygame.draw.rect(TELA, (50, 50, 50), (pos_x_barra, pos_y_barra, largura_barra, altura_barra))
            porcentagem_vida = max(0, boss.vida / boss.vida_max)
            largura_atual = int(largura_barra * porcentagem_vida)
            pygame.draw.rect(TELA, (200, 0, 0), (pos_x_barra, pos_y_barra, largura_atual, altura_barra))
            pygame.draw.rect(TELA, (255, 255, 255), (pos_x_barra, pos_y_barra, largura_barra, altura_barra), 2)
            texto_boss = fonte_hud.render("MEGA ROBOT", True, (200, 0, 0))
            TELA.blit(texto_boss, (pos_x_barra, pos_y_barra + 25))

        pygame.display.flip()

    pygame.quit()
    sys.exit()