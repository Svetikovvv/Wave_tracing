import pygame

class Button:
    def __init__(self, x, y, width, height, text, callback, tooltip=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.callback = callback
        self.tooltip = tooltip
        self.text = text
        self.font = pygame.font.SysFont("Segoe UI", 18)

    def draw(self, screen):
        shadow_offset = 3
        shadow_color = (50, 50, 50)
        button_color = (70, 130, 180)
        border_color = (255, 255, 255)

        # Рисуем тень
        shadow_rect = self.rect.copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset
        pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=8)

        # Рисуем кнопку
        pygame.draw.rect(screen, button_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=8)

        # Отрисовываем текст
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.callback()
