import pygame
import sys
import os
from game import start_game_fire

# --------- Configurações ---------
largura = 1280       # largura da janela do jogo
altura = 720         # altura da janela do jogo
FPS = 60             # frames por segundo

# Inicializa pygame
pygame.init()

# Caminho base para arquivos
base_path = os.path.dirname(os.path.abspath(__file__))

# Configuração de Som e Imagem com proteção contra erros
caminho_musica = os.path.join(base_path, "som", "somdefundo.mp3")
icon_path = os.path.join(base_path, "sprites", "Fundo.jpg")
caminho_fundo = os.path.join(base_path, "sprites", "Fundo.jpg")

# Tela
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Shooting Star")

# Tenta carregar ícone
try:
    icon = pygame.image.load(icon_path)
    pygame.display.set_icon(icon)
except Exception as e:
    print(f"Aviso: Ícone não carregado. {e}")

# Tenta carregar fundo do menu
try:
    fundo_original = pygame.image.load(caminho_fundo)
    fundo = pygame.transform.scale(fundo_original, (largura, altura))
except:
    fundo = pygame.Surface((largura, altura))
    fundo.fill((20, 20, 40)) # Azul escuro caso falhe

class Button:
    def __init__(self, text, pos, callback):
        self.text = text
        self.callback = callback
        
        self.top_color = (255, 200, 95)
        self.bottom_color = (125, 88, 59)

        # Tenta carregar fonte pixelada, senão usa padrão
        font_path = os.path.join(base_path, "PressStart2P-Regular.ttf")
        try:
            self.font = pygame.font.Font(font_path, 55)
        except:
            self.font = pygame.font.SysFont("Arial", 55, bold=True)

        self.label = self.font.render(self.text.upper(), True, (255, 255, 255))
        self.rect = self.label.get_rect(center=pos)
        self.shadow_color = (0, 0, 0, 140)
        self.shadow_offset = (4, 4)

        self.outline_color = (87, 43, 39)
        self.outline_offsets = [
            (-2, -2), (-2, 0), (-2, 2),
            (0, -2),          (0, 2),
            (2, -2),  (2, 0), (2, 2)
        ]

    def make_gradient_text(self):
        base = self.font.render(self.text.upper(), True, (255, 255, 255))
        w, h = base.get_size()
        gradient = pygame.Surface((w, h), pygame.SRCALPHA)

        for y in range(h):
            t = y / h
            r = int(self.top_color[0] * (1 - t) + self.bottom_color[0] * t)
            g = int(self.top_color[1] * (1 - t) + self.bottom_color[1] * t)
            b = int(self.top_color[2] * (1 - t) + self.bottom_color[2] * t)
            pygame.draw.line(gradient, (r, g, b), (0, y), (w, y))

        base.blit(gradient, (0, 0), special_flags=pygame.BLEND_MULT)
        return base

    def draw(self, surface, mouse_pos):
        hovered = self.rect.collidepoint(mouse_pos)
        
        # Sombra
        shadow_surf = self.make_gradient_text()
        shadow_surf.fill(self.shadow_color, special_flags=pygame.BLEND_RGBA_MIN)
        surface.blit(shadow_surf, self.rect.move(self.shadow_offset))

        # Contorno
        for ox, oy in self.outline_offsets:
            pos = self.rect.move(ox, oy)
            outline_surf = self.font.render(self.text.upper(), True, self.outline_color)
            surface.blit(outline_surf, pos)

        # Texto Principal
        gradient_text = self.make_gradient_text()
        if hovered:
            bright = pygame.Surface(gradient_text.get_size(), pygame.SRCALPHA)
            bright.fill((50, 50, 50, 0))
            gradient_text.blit(bright, (0,0), special_flags=pygame.BLEND_ADD)

        surface.blit(gradient_text, self.rect)

    def check_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.callback()

class Menu:
    def __init__(self, screen):
        self.screen = screen
        mid_x = largura // 2
        start_y = 380
        gap = 60

        self.buttons = [
            Button("play",    (mid_x, start_y), self.start_game),
            Button("options", (mid_x, start_y + gap), self.show_options),
            Button("quit",    (mid_x, start_y + 2 * gap), self.exit_game),
        ]

        self.running = True
        self.animating_circle = True
        self.circle_radius = 0
        self.circle_center = (largura // 2, altura // 2)
        self.animation_done = False

    def start_game(self):
        self.running = False
        start_game_fire() # Chama a função do jogo
         
    def show_options(self):
        print("Abrindo opções...")

    def exit_game(self):
        pygame.quit()
        sys.exit()

    def run(self):
        pygame.mixer.init()
        try:
            pygame.mixer.music.load(caminho_musica)
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)
        except:
            print("Música do menu não encontrada.")

        clock = pygame.time.Clock()
        max_radius = int((largura ** 2 + altura ** 2) ** 0.5)

        while self.running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.animation_done:
                    for btn in self.buttons:
                        btn.check_click(mouse_pos)

            self.screen.blit(fundo, (0, 0))

            # Animação de entrada
            if self.animating_circle:
                mask = pygame.Surface((largura, altura))
                mask.fill((0,0,0))
                mask.set_colorkey((255, 0, 255))
                pygame.draw.circle(mask, (255, 0, 255), self.circle_center, self.circle_radius)
                self.screen.blit(mask, (0, 0))
                self.circle_radius += 25
                if self.circle_radius > max_radius:
                    self.animating_circle = False
                    self.animation_done = True

            if self.animation_done:
                for btn in self.buttons:
                    btn.draw(self.screen, mouse_pos)

            pygame.display.flip()
            clock.tick(FPS)

        pygame.mixer.music.stop()

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((largura, altura))

    def run(self):
        menu = Menu(self.screen)
        menu.run()

if __name__ == "__main__":
    Game().run()
