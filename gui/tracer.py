from collections import deque

class Tracer:
    """
    Двунаправленная трассировка методом встречной волны.
    Вместо iteration*10 + priority каждая новая ячейка получает уникальный порядковый номер
    в порядке, в котором она извлекается из очереди BFS (соблюдая приоритет просмотра соседей).
    """

    def __init__(self, grid):
        """
        :param grid: 2D-список (копия поля), где:
                     0 – свободная клетка, 1 – препятствие,
                     2(A) и 3(B) уже заменены на 0, чтобы волна могла идти.
        """
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0

    def bidirectional_trace(self, start, finish):
        """
        Запускает двунаправленную волну: BFS от A и BFS от B.
        На каждом "уровне" мы берём все клетки очереди старта и все клетки очереди финиша,
        расширяем их соседей в порядке (вверх, вправо, вниз, влево).
        Каждая новая клетка получает уникальный порядковый номер (label_s или label_f).
        Если при расширении появляются пересечения, выбираем клетку с минимальной суммой (label_s + label_f).

        :param start: (sr, sc) координаты A
        :param finish: (fr, fc) координаты B
        :return: (wave_start, wave_finish, meeting_point)
                 wave_start[r][c] = (label_s, direction_s),
                 wave_finish[r][c] = (label_f, direction_f),
                 meeting_point – клетка пересечения или None
        """
        # Матрицы для хранения (label, direction)
        wave_start = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        wave_finish = [[None for _ in range(self.cols)] for _ in range(self.rows)]

        # Очереди BFS
        q_start = deque()
        q_finish = deque()

        sr, sc = start
        fr, fc = finish

        # Стартовые точки получают номер 0
        wave_start[sr][sc] = (0, None)
        wave_finish[fr][fc] = (0, None)
        q_start.append((sr, sc))
        q_finish.append((fr, fc))

        # Счётчики для новой нумерации
        # Каждая новая клетка, открытая волной старта, получает label_s + 1
        # Каждая новая клетка, открытая волной финиша, получает label_f + 1
        label_counter_s = 1
        label_counter_f = 1

        # Порядок просмотра соседей: верх, вправо, вниз, влево
        directions = [
            ("U", -1, 0),
            ("R", 0, 1),
            ("D", 1, 0),
            ("L", 0, -1),
        ]

        def is_valid(r, c, wave):
            return (0 <= r < self.rows and 0 <= c < self.cols
                    and self.grid[r][c] == 0
                    and wave[r][c] is None)

        best_meeting = None
        best_sum = None

        # Пока есть клетки в обеих очередях
        while q_start and q_finish:
            # 1) Расширяем волну от старта (A)
            new_start_cells = []
            for _ in range(len(q_start)):
                r, c = q_start.popleft()
                current_label_s, _ = wave_start[r][c]
                # Если мы уже дошли до B, можно проверять пересечение
                for dname, dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if is_valid(nr, nc, wave_start):
                        # Присваиваем следующий номер
                        wave_start[nr][nc] = (label_counter_s, dname)
                        label_counter_s += 1
                        q_start.append((nr, nc))
                        new_start_cells.append((nr, nc))

            # 2) Расширяем волну от финиша (B)
            new_finish_cells = []
            for _ in range(len(q_finish)):
                r, c = q_finish.popleft()
                current_label_f, _ = wave_finish[r][c]
                for dname, dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if is_valid(nr, nc, wave_finish):
                        wave_finish[nr][nc] = (label_counter_f, dname)
                        label_counter_f += 1
                        q_finish.append((nr, nc))
                        new_finish_cells.append((nr, nc))

            # 3) Проверяем пересечения среди новых клеток
            intersections = []
            for (r, c) in new_start_cells:
                if wave_finish[r][c] is not None:
                    intersections.append((r, c))
            for (r, c) in new_finish_cells:
                if wave_start[r][c] is not None:
                    intersections.append((r, c))

            if intersections:
                # Ищем минимальную сумму (label_s + label_f)
                for (r, c) in intersections:
                    label_s_val, _ = wave_start[r][c]
                    label_f_val, _ = wave_finish[r][c]
                    s = label_s_val + label_f_val
                    if best_sum is None or s < best_sum:
                        best_sum = s
                        best_meeting = (r, c)
                return wave_start, wave_finish, best_meeting

        # Если очереди опустели, пересечений нет
        return wave_start, wave_finish, None

    def step_by_step_trace(self, start, finish):
        """
        Генератор для пошаговой (по уровням) двунаправленной волны.
        На каждом "уровне" извлекаем все клетки очереди старта, затем все клетки очереди финиша,
        назначаем новые номера в порядке обнаружения. Если есть пересечения – завершаем.

        yield (iteration, wave_start, wave_finish, best_meeting)
        """
        wave_start = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        wave_finish = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        q_start = deque()
        q_finish = deque()

        sr, sc = start
        fr, fc = finish

        wave_start[sr][sc] = (0, None)
        wave_finish[fr][fc] = (0, None)
        q_start.append((sr, sc))
        q_finish.append((fr, fc))

        # Счётчики для новой нумерации
        label_counter_s = 1
        label_counter_f = 1

        directions = [
            ("U", -1, 0),
            ("R", 0, 1),
            ("D", 1, 0),
            ("L", 0, -1),
        ]

        def is_valid(r, c, wave):
            return (0 <= r < self.rows and 0 <= c < self.cols
                    and self.grid[r][c] == 0
                    and wave[r][c] is None)

        iteration = 0
        best_meeting = None
        best_sum = None

        while q_start or q_finish:
            iteration += 1

            new_start_cells = []
            for _ in range(len(q_start)):
                r, c = q_start.popleft()
                for dname, dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if is_valid(nr, nc, wave_start):
                        wave_start[nr][nc] = (label_counter_s, dname)
                        label_counter_s += 1
                        q_start.append((nr, nc))
                        new_start_cells.append((nr, nc))

            new_finish_cells = []
            for _ in range(len(q_finish)):
                r, c = q_finish.popleft()
                for dname, dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if is_valid(nr, nc, wave_finish):
                        wave_finish[nr][nc] = (label_counter_f, dname)
                        label_counter_f += 1
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

            if intersections:
                for (r, c) in intersections:
                    ls, _ = wave_start[r][c]
                    lf, _ = wave_finish[r][c]
                    total = ls + lf
                    if best_sum is None or total < best_sum:
                        best_sum = total
                        best_meeting = (r, c)
                yield iteration, wave_start, wave_finish, best_meeting
                return

            yield iteration, wave_start, wave_finish, None

        # Нет пути
        yield iteration, wave_start, wave_finish, None

    @staticmethod
    def reconstruct_path(wave, origin, meeting):
        """
        Восстанавливает путь в матрице wave (label, direction),
        двигаясь "назад" по direction: U->(r+1), R->(c-1), D->(r-1), L->(c+1).
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
