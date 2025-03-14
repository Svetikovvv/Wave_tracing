from collections import deque

class Tracer:
    """
    Класс для двунаправленной трассировки (bidirectional wave),
    где при появлении пересечений в одной итерации выбирается то,
    у которого минимальная сумма приоритетов (wave_start[r][c] + wave_finish[r][c]).
    """

    def __init__(self, grid):
        """
        :param grid: 2D-список (копия поля), где:
                     0 – свободная клетка, 1 – препятствие,
                     2(A) и 3(B) здесь уже заменены на 0, чтобы волна могла идти.
        """
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0

    def bidirectional_trace(self, start, finish):
        """
        Выполняет двунаправленный BFS. На каждом уровне:
          1) Расширяет волны старта
          2) Расширяет волны финиша
          3) Ищет новые пересечения
             Если они есть, выбирает клетку с минимальной суммой composite_value
             (wave_start[r][c] + wave_finish[r][c]) и останавливается.

        :param start: (r, c) координаты A
        :param finish: (r, c) координаты B
        :return: (wave_start, wave_finish, best_meeting)
                 wave_start[r][c] = (cv, dname)
                 wave_finish[r][c] = (cv, dname)
                 best_meeting – клетка пересечения или None
        """
        # Приоритет направлений
        direction_priority = {"U": 1, "R": 2, "D": 3, "L": 4}

        # Матрицы для (composite_value, direction)
        wave_start = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        wave_finish = [[None for _ in range(self.cols)] for _ in range(self.rows)]

        q_start = deque()
        q_finish = deque()

        s_r, s_c = start
        f_r, f_c = finish
        wave_start[s_r][s_c] = (0, None)
        wave_finish[f_r][f_c] = (0, None)
        q_start.append(start)
        q_finish.append(finish)

        iteration = 0

        def is_valid(r, c, visited):
            return (0 <= r < self.rows and 0 <= c < self.cols
                    and self.grid[r][c] == 0
                    and visited[r][c] is None)

        # Можно упорядочить направления в любом порядке (U, R, D, L) и т.д.
        directions = [
            ("U", -1, 0),
            ("R", 0, 1),
            ("D", 1, 0),
            ("L", 0, -1)
        ]

        while q_start and q_finish:
            iteration += 1

            # 1) Расширяем волну старта
            new_start_cells = []
            for _ in range(len(q_start)):
                r, c = q_start.popleft()
                for dname, dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if is_valid(nr, nc, wave_start):
                        cv = iteration * 10 + direction_priority[dname]
                        wave_start[nr][nc] = (cv, dname)
                        q_start.append((nr, nc))
                        new_start_cells.append((nr, nc))

            # 2) Расширяем волну финиша
            new_finish_cells = []
            for _ in range(len(q_finish)):
                r, c = q_finish.popleft()
                for dname, dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if is_valid(nr, nc, wave_finish):
                        cv = iteration * 10 + direction_priority[dname]
                        wave_finish[nr][nc] = (cv, dname)
                        q_finish.append((nr, nc))
                        new_finish_cells.append((nr, nc))

            # 3) Проверяем новые пересечения
            intersections = []
            for (r, c) in new_start_cells:
                if wave_finish[r][c] is not None:
                    intersections.append((r, c))
            for (r, c) in new_finish_cells:
                if wave_start[r][c] is not None:
                    intersections.append((r, c))

            if intersections:
                # Выбираем среди них клетку с минимальной суммой
                best = None
                best_sum = None
                for (r, c) in intersections:
                    cv_s, _ = wave_start[r][c]
                    cv_f, _ = wave_finish[r][c]
                    s = cv_s + cv_f
                    if best_sum is None or s < best_sum:
                        best_sum = s
                        best = (r, c)

                return wave_start, wave_finish, best

        # Если не нашли пересечений и очереди исчерпаны
        return wave_start, wave_finish, None

    def step_by_step_trace(self, start, finish):
        """
        Генератор: на каждом "шаге" (итерации) расширяем волны старта и финиша,
        затем проверяем новые пересечения. Если пересечения есть, выбираем минимальное
        и завершаем. Если нет – продолжаем.
        """
        from collections import deque
        direction_priority = {"U": 1, "R": 2, "D": 3, "L": 4}

        wave_start = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        wave_finish = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        q_start = deque()
        q_finish = deque()

        s_r, s_c = start
        f_r, f_c = finish
        wave_start[s_r][s_c] = (0, None)
        wave_finish[f_r][f_c] = (0, None)
        q_start.append(start)
        q_finish.append(finish)

        iteration = 0

        def is_valid(r, c, visited):
            return (0 <= r < self.rows and 0 <= c < self.cols
                    and self.grid[r][c] == 0
                    and visited[r][c] is None)

        directions = [
            ("U", -1, 0),
            ("R", 0, 1),
            ("D", 1, 0),
            ("L", 0, -1)
        ]

        # Пока есть клетки для расширения
        while q_start or q_finish:
            iteration += 1

            new_start_cells = []
            for _ in range(len(q_start)):
                r, c = q_start.popleft()
                for dname, dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if is_valid(nr, nc, wave_start):
                        cv = iteration * 10 + direction_priority[dname]
                        wave_start[nr][nc] = (cv, dname)
                        q_start.append((nr, nc))
                        new_start_cells.append((nr, nc))

            new_finish_cells = []
            for _ in range(len(q_finish)):
                r, c = q_finish.popleft()
                for dname, dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if is_valid(nr, nc, wave_finish):
                        cv = iteration * 10 + direction_priority[dname]
                        wave_finish[nr][nc] = (cv, dname)
                        q_finish.append((nr, nc))
                        new_finish_cells.append((nr, nc))

            # Проверяем пересечения
            intersections = []
            for (r, c) in new_start_cells:
                if wave_finish[r][c] is not None:
                    intersections.append((r, c))
            for (r, c) in new_finish_cells:
                if wave_start[r][c] is not None:
                    intersections.append((r, c))

            # Возвращаем текущее состояние
            if intersections:
                # Выбираем лучшее пересечение
                best = None
                best_sum = None
                for (r, c) in intersections:
                    cv_s, _ = wave_start[r][c]
                    cv_f, _ = wave_finish[r][c]
                    s = cv_s + cv_f
                    if best_sum is None or s < best_sum:
                        best_sum = s
                        best = (r, c)

                yield iteration, wave_start, wave_finish, best
                return  # Останавливаемся

            # Если нет пересечений, просто возвращаем состояние
            yield iteration, wave_start, wave_finish, None

        # Если очереди исчерпаны, путь не найден
        yield iteration, wave_start, wave_finish, None


    @staticmethod
    def reconstruct_path(wave, origin, meeting):
        """
        Восстанавливает путь в матрице wave от origin до meeting.
        wave[r][c] = (composite_value, direction).
        """
        path = []
        r, c = meeting
        while (r, c) != origin:
            path.append((r, c))
            data = wave[r][c]
            if data is None:
                break
            _, direction = data
            if direction is None:
                break
            if direction == "U":
                r += 1
            elif direction == "D":
                r -= 1
            elif direction == "L":
                c += 1
            elif direction == "R":
                c -= 1
        path.append(origin)
        path.reverse()
        return path
