import pygame

class TextInput:
    def __init__(self, x, y, width, height, font_size=24, initial_text=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.base_color = (240, 240, 240)
        self.active_color = (255, 255, 255)
        self.text = initial_text
        self.font = pygame.font.SysFont("Segoe UI", font_size)
        self.active = True
        self.done = False
        self.cursor_visible = True
        self.cursor_switch_ms = 500
        self.time_accumulator = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.done = True
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode

    def update(self, dt):
        self.time_accumulator += dt
        if self.time_accumulator >= self.cursor_switch_ms:
            self.cursor_visible = not self.cursor_visible
            self.time_accumulator %= self.cursor_switch_ms

    def draw(self, screen):
        bg_color = self.active_color if self.active else self.base_color
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        border_color = (100, 100, 100)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=8)
        txt_surf = self.font.render(self.text, True, (0, 0, 0))
        screen.blit(txt_surf, (self.rect.x + 10, self.rect.y + (self.rect.height - txt_surf.get_height()) // 2))
        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 10 + txt_surf.get_width() + 2
            cursor_y = self.rect.y + (self.rect.height - self.font.get_height()) // 2
            pygame.draw.line(screen, (0, 0, 0), (cursor_x, cursor_y), (cursor_x, cursor_y + self.font.get_height()), 2)
