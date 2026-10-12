import random

# Элементы рендеринга
RENDER_ELEMENTS = {
    "wall_visible": "🧱",
    "wall_hidden": "🟩",
    "floor_visible": "  ",
    "floor_hidden": "⬛",
    "money": "₽ ",          # Иконка денег на карте
    "loot": "📦"           # Любой другой предмет из инвентаря
}


class Maze:
    def __init__(self, grid: list[list[bool]], displayable: list[list[str]]):
        """
        Инициализация лабиринта.
        grid: 2D матрица, где True - стена, False - проход.
        displayable: 2D матрица со стилизованными символами (из генератора).
        """
        self.grid = grid
        self.displayable = displayable
        self.height = len(grid)
        self.width = len(grid[0]) if self.height > 0 else 0

    def get_random_empty_position(self) -> tuple[int, int]:
        """
        Находит случайную пустую клетку в лабиринте.
        Возвращает кортеж (logical_x, logical_y).
        """
        empty_cells = []
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if not self.grid[y][x]:
                    logical_x = x - 1
                    logical_y = y - 1
                    empty_cells.append((logical_x, logical_y))
        
        return random.choice(empty_cells)

    def is_wall(self, logical_x: int, logical_y: int) -> bool:
        """Проверяет стену по логическим координатам персонажа (смещение +1)."""
        array_x = logical_x + 1
        array_y = logical_y + 1

        if array_x < 0 or array_x >= self.width or array_y < 0 or array_y >= self.height:
            return True
            
        return self.grid[array_y][array_x]

    def _is_visible_straight(self, char_x: int, char_y: int, target_x: int, target_y: int) -> bool:
        """Проверяет видимость СТРОГО пустого прохода по прямой линии."""
        if char_x != target_x and char_y != target_y:
            return False

        if char_y == target_y:
            step = 1 if target_x > char_x else -1
            for x in range(char_x + step, target_x + step, step):
                if self.grid[char_y][x]:
                    return False

        if char_x == target_x:
            step = 1 if target_y > char_y else -1
            for y in range(char_y + step, target_y + step, step):
                if self.grid[y][char_x]:
                    return False

        return True

    def _should_reveal_wall(self, char_x: int, char_y: int, wall_x: int, wall_y: int, vision_radius: int) -> bool:
        """Проверяет, должна ли стена быть видимой (есть ли рядом освещенный проход)."""
        neighbors = [
            (wall_x + 1, wall_y), (wall_x - 1, wall_y),
            (wall_x, wall_y + 1), (wall_x, wall_y - 1)
        ]

        for nx, ny in neighbors:
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if not self.grid[ny][nx]:
                    if abs(char_x - nx) + abs(char_y - ny) <= vision_radius:
                        if self._is_visible_straight(char_x, char_y, nx, ny):
                            return True
        return False

    def display(self, active_player, characters: list, items_on_map: dict, vision_radius: int = 5, fog_of_war: bool = True):
        """Отрисовывает лабиринт с учетом персонажей и предметов на полу."""
        char_array_x = active_player.x + 1
        char_array_y = active_player.y + 1
        
        char_map = {}
        for c in characters:
            char_map[(c.x + 1, c.y + 1)] = c.icon

        for y in range(self.height):
            row_str = ""
            for x in range(self.width):
                if not fog_of_war:
                    is_visible = True
                else:
                    manhattan_dist = abs(char_array_x - x) + abs(char_array_y - y)
                    is_visible = (manhattan_dist <= vision_radius and 
                                  self._is_visible_straight(char_array_x, char_array_y, x, y))

                logical_pos = (x - 1, y - 1)

                is_active_player = (x == char_array_x and y == char_array_y)
                if (x, y) in char_map and (is_visible or is_active_player):
                    row_str += char_map[(x, y)]
                
                elif logical_pos in items_on_map and is_visible:
                    row_str += items_on_map[logical_pos].icon
                
                elif self.grid[y][x]:
                    if not fog_of_war:
                        row_str += RENDER_ELEMENTS["wall_visible"]
                    elif self._should_reveal_wall(char_array_x, char_array_y, x, y, vision_radius):
                        row_str += RENDER_ELEMENTS["wall_visible"]
                    else:
                        row_str += RENDER_ELEMENTS["wall_hidden"]
                
                else:
                    if is_visible:
                        row_str += RENDER_ELEMENTS["floor_visible"]
                    else:
                        row_str += RENDER_ELEMENTS["floor_hidden"]
                        
            print(row_str)
        print()
