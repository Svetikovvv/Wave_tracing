import pygame

class MenuBar:
    def __init__(self, width, menu_bar_height, theme):
        self.width = width
        self.menu_bar_height = menu_bar_height
        self.theme = theme
        self.menu_items = {
            "Файл": [
                ("Новый файл", None),
                ("Открыть", None),
                ("Сохранить", None),
                ("Выход", None)
            ],
            "Правка": [
                ("Очистить всё", None),
                ("Очистить преп.", None),
                ("Очистить A/B", None),
                ("Размер", None)
            ],
            "Трассировка": [
                ("Трасс.", None),
                ("Пошаг", None),
                ("Стоп", None)
            ]
        }
        self.menu_positions = {}
        self.active_menu = None
        self.active_menu_items = []

    def set_callbacks(self, callbacks):
        # callbacks – словарь, сопоставляющий название пункта меню с функцией
        for menu, items in self.menu_items.items():
            new_items = []
            for (text, _) in items:
                new_items.append((text, callbacks.get(text)))
            self.menu_items[menu] = new_items

    def draw(self, screen):
        menu_rect = pygame.Rect(0, 0, self.width, self.menu_bar_height)
        pygame.draw.rect(screen, self.theme["menu_bg"], menu_rect)
        font = pygame.font.SysFont("Segoe UI", 18)
        padding = 10
        x_offset = padding
        self.menu_positions = {}
        for menu_title in self.menu_items.keys():
            text_surf = font.render(menu_title, True, self.theme["menu_text"])
            text_rect = text_surf.get_rect(topleft=(x_offset, (self.menu_bar_height - text_surf.get_height()) // 2))
            screen.blit(text_surf, text_rect)
            self.menu_positions[menu_title] = pygame.Rect(x_offset, 0, text_rect.width, self.menu_bar_height)
            x_offset += text_rect.width + 2 * padding
        if self.active_menu:
            self.draw_dropdown(screen, self.active_menu)

    def draw_dropdown(self, screen, menu_title):
        items = self.menu_items[menu_title]
        font = pygame.font.SysFont("Segoe UI", 16)
        dropdown_width = 150
        item_height = 25
        menu_rect = self.menu_positions[menu_title]
        dropdown_x = menu_rect.x
        dropdown_y = menu_rect.bottom
        dropdown_rect = pygame.Rect(dropdown_x, dropdown_y, dropdown_width, item_height * len(items))
        pygame.draw.rect(screen, self.theme["menu_bg"], dropdown_rect)
        pygame.draw.rect(screen, self.theme["grid_color"], dropdown_rect, 1)
        self.active_menu_items = []
        for index, (item_text, callback) in enumerate(items):
            item_rect = pygame.Rect(dropdown_x, dropdown_y + index * item_height, dropdown_width, item_height)
            if item_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, self.theme["menu_hover"], item_rect)
            text_surf = font.render(item_text, True, self.theme["menu_text"])
            text_rect = text_surf.get_rect()
            text_rect.centery = item_rect.centery
            text_rect.x = item_rect.x + 5
            screen.blit(text_surf, text_rect)
            self.active_menu_items.append((item_text, item_rect, callback))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for title, rect in self.menu_positions.items():
                if rect.collidepoint(pos):
                    self.active_menu = None if self.active_menu == title else title
                    return True
            if self.active_menu:
                for item_text, item_rect, callback in self.active_menu_items:
                    if item_rect.collidepoint(pos):
                        if callback:
                            callback()
                        self.active_menu = None
                        return True
                self.active_menu = None
        return False
