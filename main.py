import pygame
import sys
import os
# --------- Configurações ---------
largura = 1280         # largura da janela do jogo
altura = 720           # altura da janela do jogo
FPS = 60               # frames por segundo (velocidade do loop)

# Caminho da música (está uma pasta acima, dentro da pasta 'audio')
base_path = os.path.dirname(os.path.abspath(__file__))
caminho_musica = os.path.join(base_path, "som", "somdefundo.mp3")

# Cores usadas no jogo
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HIGHLIGHT = (255, 255, 0)  # amarelo para destacar os botões

# Inicializa todos os módulos do pygame (exceto mixer que será inicializado no menu)
pygame.init()

# Caminho do ícone (volta uma pasta e acessa teste.png)
icon_path = os.path.join(os.path.dirname(__file__),  "sprites", "Fundo.jpg")
icon = pygame.image.load(icon_path)
pygame.display.set_icon(icon)
pygame.display.set_caption("Shooting Star")

# Fonte usada nos botões ##### Procurar fonte ideal #####
FONT_BUTTON = pygame.font.SysFont("Poppins", 67)

# Cria a janela do jogo com o tamanho definido
tela = pygame.display.set_mode((largura, altura))

# Carrega a imagem de fundo do menu e ajusta para o tamanho da janela
caminho_fundo = os.path.join(os.path.dirname(__file__), "sprites", "Fundo.jpg")
fundo_original = pygame.image.load(caminho_fundo)
fundo = pygame.transform.scale(fundo_original, (largura, altura))


class Button:
    def __init__(self, text, pos, callback):
        self.text = text
        self.callback = callback
        
        # Cores do degradê
        self.top_color = (255, 200, 95)
        self.bottom_color = (125, 88, 59)

        # Fonte pixelada
        font_path = os.path.join(os.path.dirname(__file__), "PressStart2P-Regular.ttf")
        self.font = pygame.font.Font(font_path, 55)

        # Render inicial (será sobrescrito pelo degradê depois)
        self.label = self.font.render(self.text.upper(), True, (255, 255, 255))
        self.rect = self.label.get_rect(center=pos)
        # sombra do texto
        self.shadow_color = (0, 0, 0, 140)  # preto translúcido
        self.shadow_offset = (4, 4)         # deslocamento da sombra

        # contorno estilo pixel art
        self.outline_color = (87, 43, 39)
        self.outline_offsets = [
            (-2, -2), (-2, 0), (-2, 2),
            (0, -2),          (0, 2),
            (2, -2),  (2, 0), (2, 2)
        ]

    def make_gradient_text(self):
        """Renderiza o texto com degradê vertical."""
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

        # Efeito de highlight (deixa o degradê mais claro)
        if hovered:
            bright = pygame.Surface(self.label.get_size(), pygame.SRCALPHA)
            bright.fill((40, 40, 40, 0))  # efeito leve
        else:
            bright = None

        shadow_surf = self.make_gradient_text()
        shadow_surf.fill(self.shadow_color, special_flags=pygame.BLEND_RGBA_MIN)
        shadow_rect = self.rect.move(self.shadow_offset)
        surface.blit(shadow_surf, shadow_rect)

        # contorno estilo pixel art
        for ox, oy in self.outline_offsets:
            pos = self.rect.move(ox, oy)
            outline_surf = self.font.render(self.text.upper(), True, self.outline_color)
            surface.blit(outline_surf, pos)

        # Renderiza o degradê
        gradient_text = self.make_gradient_text()

        # Se está com highlight, aplica brilho
        if hovered:
            gradient_text.blit(bright, (0, 0), special_flags=pygame.BLEND_ADD)

        # desenhar o texto final
        surface.blit(gradient_text, self.rect)

    def check_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.callback()

class Menu:
    """Classe que gerencia o menu principal do jogo."""
    def __init__(self, screen):
        self.screen = screen
        mid_x = largura // 2      # posição horizontal central para os botões
        start_y = 380             # posição vertical inicial do primeiro botão
        gap = 60                  # espaçamento vertical entre os botões

        # Cria botões do menu com suas posições e funções
        self.buttons = [
            Button("play",    (mid_x, start_y), self.start_game),
            Button("options", (mid_x, start_y + gap), self.show_options),
            Button("quit",    (mid_x, start_y + 2 * gap), self.exit_game),
        ]

        self.running = True

        # Variáveis para animação do círculo de transição do menu
        self.animating_circle = True
        self.circle_radius = 0
        self.circle_center = (largura // 2, altura // 2)

        self.animation_done = False  # indica se animação terminou

    def start_game(self):
        print("Iniciando o jogo...")
        self.running = False  # fecha o menu para iniciar o jogo

    def show_options(self):
        print("Abrindo opções...")  # placeholder para futura tela de opções

    def exit_game(self):
        pygame.quit()
        sys.exit()  # encerra o programa

    def run(self):
        # Inicializa o mixer e toca a música do menu em loop infinito
        pygame.mixer.init()
        pygame.mixer.music.load(caminho_musica)
        pygame.mixer.music.set_volume(0.3)  # volume entre 0.0 e 1.0
        pygame.mixer.music.play(-1)         # -1 para tocar em loop

        clock = pygame.time.Clock()
        max_radius = int((largura ** 2 + altura ** 2) ** 0.5)  # diagonal da tela para animação

        while self.running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()

                # Só permite clicar nos botões após animação acabar
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.animation_done:
                    for btn in self.buttons:
                        btn.check_click(mouse_pos)

            # Desenha o fundo do menu
            self.screen.blit(fundo, (0, 0))

            # Animação do círculo que revela o menu
            if self.animating_circle:
                mask = pygame.Surface((largura, altura))
                mask.fill(BLACK)
                mask.set_colorkey((255, 0, 255))  # cor transparente da máscara
                pygame.draw.circle(mask, (255, 0, 255), self.circle_center, self.circle_radius)
                self.screen.blit(mask, (0, 0))

                self.circle_radius += 20  # aumenta o raio do círculo

                if self.circle_radius > max_radius:
                    self.animating_circle = False
                    self.animation_done = True

            # Após animação, desenha os botões e permite interação
            if self.animation_done:
                for btn in self.buttons:
                    btn.draw(self.screen, mouse_pos)

            pygame.display.flip()
            clock.tick(FPS)

        # Para a música quando o menu fechar
        pygame.mixer.music.stop()


class Game:
    """Classe principal do jogo."""

    def __init__(self):
        self.screen = pygame.display.set_mode((largura, altura))

    def run(self):
        # Executa o menu antes do jogo começar
        menu = Menu(self.screen)
        menu.run()
        self.game_loop()

    def game_loop(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Limpa a tela com cor cinza escura
            self.screen.fill((30, 30, 30))

            # Aqui vai o código do jogo propriamente dito

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()
       


if __name__ == "__main__":
    Game().run()