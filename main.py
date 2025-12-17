import pygame
import sys
import os
from game import start_game_fire

# --------- Configurações ---------
largura = 1280
altura = 720
FPS = 60

# Caminhos dos arquivos
base_path = os.path.dirname(os.path.abspath(__file__))
caminho_musica = os.path.join(base_path, "som", "somdefundo.mp3")
font_path = os.path.join(base_path, "PressStart2P-Regular.ttf")

# Cores
WHITE = (255, 255, 255)
HIGHLIGHT = (255, 255, 0)
BLACK = (0, 0, 0)
# Cores usadas para o efeito de texto dourado/pixel art:
TOP_GOLD = (255, 200, 95)
BOTTOM_BROWN = (125, 88, 59)
OUTLINE_BROWN = (87, 43, 39)
SHADOW_COLOR = (0, 0, 0, 140)

# Inicializa todos os módulos do pygame
pygame.init()

# Carrega fundos
caminho_fundo_menu = os.path.join(base_path, "sprites", "Fundo.jpg")
fundo_original_menu = pygame.image.load(caminho_fundo_menu)
fundo_menu = pygame.transform.scale(fundo_original_menu, (largura, altura))

# Carrega o fundo de Game Over (OVER.JPEG)
caminho_fundo_game_over = os.path.join(base_path, "sprites", "over.png")
try:
    fundo_original_game_over = pygame.image.load(caminho_fundo_game_over)
    fundo_game_over = pygame.transform.scale(fundo_original_game_over, (largura, altura))
except (pygame.error, FileNotFoundError) as e:
    print(f"Erro ao carregar over.png: {e}. Usando Fundo.jpg como fallback.")
    fundo_game_over = fundo_menu

# Cria a janela do jogo
tela = pygame.display.set_mode((largura, altura))

# --- Funções Auxiliares de Renderização de Texto ---

def get_font(size):
    """Tenta carregar a fonte pixelizada, com fallback para fonte padrão."""
    try:
        return pygame.font.Font(font_path, size)
    except:
        return pygame.font.SysFont("comicsansms", size)

def render_gradient_text(font, text, top_color, bottom_color):
    """Renderiza o texto com degradê vertical (usado para o efeito 'ouro')."""
    base = font.render(text.upper(), True, (255, 255, 255))
    w, h = base.get_size()

    gradient = pygame.Surface((w, h), pygame.SRCALPHA)

    for y in range(h):
        t = y / h
        r = int(top_color[0] * (1 - t) + bottom_color[0] * t)
        g = int(top_color[1] * (1 - t) + bottom_color[1] * t)
        b = int(top_color[2] * (1 - t) + bottom_color[2] * t)

        pygame.draw.line(gradient, (r, g, b), (0, y), (w, y))

    base.blit(gradient, (0, 0), special_flags=pygame.BLEND_MULT)
    return base

def render_pixel_text(surface, text, size, center_pos, shadow_offset=(4, 4)):
    """
    Renderiza o texto completo com degradê, sombra e contorno,
    replicando o estilo dos botões.
    """
    font = get_font(size)
   
    # 1. Pré-renderiza a base do texto com degradê
    gradient_text_base = render_gradient_text(font, text, TOP_GOLD, BOTTOM_BROWN)
    text_rect = gradient_text_base.get_rect(center=center_pos)

    # 2. Desenha o contorno (outline)
    outline_offsets = [
        (-2, -2), (-2, 0), (-2, 2), (0, -2), (0, 2), (2, -2), (2, 0), (2, 2)
    ]
    for ox, oy in outline_offsets:
        pos = text_rect.move(ox, oy)
        outline_surf = font.render(text.upper(), True, OUTLINE_BROWN)
        surface.blit(outline_surf, pos)
       
    # 3. Desenha a sombra
    shadow_surf = render_gradient_text(font, text, TOP_GOLD, BOTTOM_BROWN)
    shadow_surf.fill(SHADOW_COLOR, special_flags=pygame.BLEND_RGBA_MIN)
    shadow_rect = text_rect.move(shadow_offset)
    surface.blit(shadow_surf, shadow_rect)
   
    # 4. Desenha o texto principal
    surface.blit(gradient_text_base, text_rect)


class Button:
    # A classe Button usa a lógica de renderização embutida para manter a compatibilidade.
    def __init__(self, text, pos, callback):
        self.text = text
        self.callback = callback
       
        self.top_color = TOP_GOLD
        self.bottom_color = BOTTOM_BROWN

        self.font = get_font(55)

        self.label = self.font.render(self.text.upper(), True, (255, 255, 255))
        self.rect = self.label.get_rect(center=pos)
        self.shadow_color = SHADOW_COLOR
        self.shadow_offset = (4, 4)

        self.outline_color = OUTLINE_BROWN
        self.outline_offsets = [
            (-2, -2), (-2, 0), (-2, 2), (0, -2), (0, 2), (2, -2), (2, 0), (2, 2)
        ]

    def make_gradient_text(self):
        return render_gradient_text(self.font, self.text, self.top_color, self.bottom_color)

    def draw(self, surface, mouse_pos):
        hovered = self.rect.collidepoint(mouse_pos)
        bright = None
        if hovered:
            bright = pygame.Surface(self.label.get_size(), pygame.SRCALPHA)
            bright.fill((40, 40, 40, 0))

        shadow_surf = self.make_gradient_text()
        shadow_surf.fill(self.shadow_color, special_flags=pygame.BLEND_RGBA_MIN)
        shadow_rect = self.rect.move(self.shadow_offset)
        surface.blit(shadow_surf, shadow_rect)

        for ox, oy in self.outline_offsets:
            pos = self.rect.move(ox, oy)
            outline_surf = self.font.render(self.text.upper(), True, self.outline_color)
            surface.blit(outline_surf, pos)

        gradient_text = self.make_gradient_text()

        if hovered:
            gradient_text.blit(bright, (0, 0), special_flags=pygame.BLEND_ADD)

        surface.blit(gradient_text, self.rect)

    def check_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.callback()


class Menu:
    # A classe Menu permanece como antes.
    def __init__(self, screen):
        self.screen = screen
        mid_x = largura // 2
        start_y = 380
        gap = 60

        self.buttons = [
            Button("play", (mid_x, start_y), self.start_game),
            Button("options", (mid_x, start_y + gap), self.show_options),
            Button("quit", (mid_x, start_y + 2 * gap), self.exit_game),
        ]

        self.running = True
        self.animating_circle = True
        self.circle_radius = 0
        self.circle_center = (largura // 2, altura // 2)
        self.animation_done = False

    def start_game(self):
        self.running = False
       
    def show_options(self):
        print("Abrindo opções...")

    def exit_game(self):
        pygame.quit()
        sys.exit()

    def run(self):
        pygame.mixer.init()
        pygame.mixer.music.load(caminho_musica)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)

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

            self.screen.blit(fundo_menu, (0, 0))

            if self.animating_circle:
                mask = pygame.Surface((largura, altura))
                mask.fill(BLACK)
                mask.set_colorkey((255, 0, 255))
                pygame.draw.circle(mask, (255, 0, 255), self.circle_center, self.circle_radius)
                self.screen.blit(mask, (0, 0))

                self.circle_radius += 20

                if self.circle_radius > max_radius:
                    self.animating_circle = False
                    self.animation_done = True

            if self.animation_done:
                for btn in self.buttons:
                    btn.draw(self.screen, mouse_pos)

            pygame.display.flip()
            clock.tick(FPS)

        pygame.mixer.music.stop()


class GameOverScreen:
    """Tela de Fim de Jogo (Game Over) com fundo e fonte pixelizada customizados."""
    def __init__(self, screen, final_score):
        self.screen = screen
        self.final_score = final_score
        self.running = True
        self.clock = pygame.time.Clock()
       
    def run(self):
        while self.running:
            self.clock.tick(FPS)
           
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
               
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        self.running = False
                        return "restart"
                    if event.key == pygame.K_s or event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
           
            # Desenho da tela de Game Over
            self.screen.blit(fundo_game_over, (0, 0)) # USANDO O OVER.JPEG

            # Título FIM DE JOGO
            render_pixel_text(
                self.screen,
                "FIM DE JOGO",
                80,
                (largura // 2, altura // 4)
            )
           
            # Pontuação Final
            render_pixel_text(
                self.screen,
                f"PONTOS FINAIS: {self.final_score}",
                30,
                (largura // 2, altura // 2)
            )

            # Mensagem para continuar/sair (Texto simples, usando HIGHLIGHT)
            # Como a mensagem inferior não tem o efeito 3D na imagem original,
            # usaremos um simples draw_text para o controle.
            msg = "Pressione 'C' para Continuar ou 'S' / 'ESC' para Sair"
            font_tiny = get_font(20)
            msg_text = font_tiny.render(msg, True, HIGHLIGHT)
            msg_rect = msg_text.get_rect(center=(largura // 2, altura * 3 // 4))
            self.screen.blit(msg_text, msg_rect)
           
            pygame.display.flip()
       
        return "quit"

class Game:
    """Classe principal do jogo que gerencia o fluxo de telas."""

    def __init__(self):
        self.screen = pygame.display.set_mode((largura, altura))

    def run(self):
       
        while True:
            # 1. Executa o Menu
            menu = Menu(self.screen)
            menu.run()
           
            # 2. Executa o loop do Jogo. Retorna a pontuação.
            final_score = self.game_loop()
           
            # 3. Executa a tela de Game Over
            if final_score is not None:
                game_over_screen = GameOverScreen(self.screen, final_score)
                action = game_over_screen.run()
               
                if action == "restart":
                    continue
                else:
                    pass

    def game_loop(self):
        # Chama a função principal do jogo em game.py
        pontos = start_game_fire()
        return pontos

if __name__ == "__main__":
    Game().run()