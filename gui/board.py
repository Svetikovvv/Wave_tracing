import pygame

class Board:
    def __init__(self, rect, grid_size, theme):
        self.rect = rect
        self.grid_size = grid_size
        self.theme = theme
        self.rows = grid_size
        self.cols = grid_size
        self.cell_size = self.rect.width // self.cols
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]


        # Изменение: добавляем атрибуты для хранения данных волн
        self.wave_start = None
        self.wave_finish = None

    def draw(self, screen):
        pygame.draw.rect(screen, self.theme["board_bg"], self.rect, border_radius=10)

        # Шрифт для вывода составного значения
        font_small = pygame.font.SysFont("Segoe UI", max(12, self.cell_size // 4))
        # Изменение: новая карта стрелок (переставляем: U→"↓", D→"↑", R→"←", L→"→")
        arrow_map = {"U": "↓", "R": "←", "D": "↑", "L": "→"}

        for row in range(self.rows):
            for col in range(self.cols):
                cell_rect = pygame.Rect(
                    self.rect.x + col * self.cell_size,
                    self.rect.y + row * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                cell_val = self.board[row][col]

                # Рисуем фон клетки
                if cell_val == 1:
                    pygame.draw.rect(screen, (160, 160, 160), cell_rect, border_radius=5)
                elif cell_val == 2:
                    pygame.draw.rect(screen, self.theme["board_bg"], cell_rect)
                    self.draw_text(screen, "A", cell_rect)
                elif cell_val == 3:
                    pygame.draw.rect(screen, self.theme["board_bg"], cell_rect)
                    self.draw_text(screen, "B", cell_rect)
                else:
                    pygame.draw.rect(screen, self.theme["board_bg"], cell_rect)

                # Отображаем данные волны только если клетка не является стартом/финишем
                if cell_val not in (2, 3):
                    # Волна старта
                    if self.wave_start:
                        data_s = self.wave_start[row][col]
                        if data_s is not None:
                            composite_value, direction_s = data_s
                            text = f"{composite_value}"
                            text_surf = font_small.render(text, True, (0, 0, 0))
                            text_rect = text_surf.get_rect(topright=(cell_rect.right - 2, cell_rect.y + 2))
                            screen.blit(text_surf, text_rect)
                            overlay_s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                            overlay_s.fill((200, 255, 200, 100))
                            screen.blit(overlay_s, cell_rect)
                            if direction_s:
                                arrow_symbol = arrow_map.get(direction_s, "")
                                arrow_surf = font_small.render(arrow_symbol, True, (0, 0, 0))
                                arrow_rect = arrow_surf.get_rect(center=cell_rect.center)
                                screen.blit(arrow_surf, arrow_rect)

                    # Волна финиша
                    if self.wave_finish:
                        data_f = self.wave_finish[row][col]
                        if data_f is not None:
                            composite_value, direction_f = data_f
                            text = f"{composite_value}"
                            text_surf = font_small.render(text, True, (0, 0, 0))
                            text_rect = text_surf.get_rect(topright=(cell_rect.right - 2, cell_rect.y + 20))
                            screen.blit(text_surf, text_rect)
                            overlay_f = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                            overlay_f.fill((200, 220, 255, 100))
                            screen.blit(overlay_f, cell_rect)
                            if direction_f:
                                arrow_symbol = arrow_map.get(direction_f, "")
                                arrow_surf = font_small.render(arrow_symbol, True, (0, 0, 0))
                                arrow_rect = arrow_surf.get_rect(center=cell_rect.center)
                                screen.blit(arrow_surf, arrow_rect)

                # Отрисовка итогового пути:
                if cell_val == 4:
                    # Обычный путь (например, желтый) – можно оставить для полного трассирования
                    overlay_path = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                    overlay_path.fill((255, 255, 0, 128))
                    screen.blit(overlay_path, cell_rect)
                elif cell_val == 5:
                    # Изменение: новый цвет для итогового пути при пошаговой трассировке (например, оранжевый)
                    overlay_path = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                    overlay_path.fill((255, 165, 0, 128))
                    screen.blit(overlay_path, cell_rect)

                pygame.draw.rect(screen, self.theme["grid_color"], cell_rect, 1)



    def draw_text(self, screen, text, rect):
        font = pygame.font.SysFont("Segoe UI", self.cell_size - 4)
        text_surf = font.render(text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

    def handle_click(self, pos, mode, combined_step):
        col = (pos[0] - self.rect.x) // self.cell_size
        row = (pos[1] - self.rect.y) // self.cell_size
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return mode, combined_step
        if mode == "obstacle":
            if self.board[row][col] in (2, 3):
                return mode, combined_step
            self.board[row][col] = 1 if self.board[row][col] == 0 else 0
        elif mode == "combined":
            if combined_step == "start" and self.board[row][col] == 0:
                self.board[row][col] = 2
                combined_step = "end"
            elif combined_step == "end" and self.board[row][col] == 0:
                self.board[row][col] = 3
                mode, combined_step = None, None
        return mode, combined_step

    def update_size(self, new_size):
        self.grid_size = new_size
        self.rows = new_size
        self.cols = new_size
        self.cell_size = self.rect.width // self.cols
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
