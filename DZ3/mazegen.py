import random
from game_objects import LockedCache, LockedExit, Loot, MoneyPile, Portal, ScaldingPipe

# расширяемая таблица предметов
# Формат: "id_предмета": (тип_для_рендера, название, базовый_шанс_спавна)
LOOT_TABLE = {
    "money_small":          ("money", "Пачка рублей",       0.050, ' '),     # 5% шанс на каждую пустую клетку
    "money_bag":            ("money", "Мешок с деньгами",   0.020, ' '),   # 2% шанс
    "paste":                ("loot",  "Техническая паста",   0.010, "🧴"),      # 1% шанс
    "fork":                 ("loot",  "Столовая вилка",     0.010, "🍴"),     # 1% шанс
    "safety_vest":          ("loot",  "Жилет электрика",    0.015, "🦺"),       # 1.5% шанс
    "energy_drink":         ("loot",  "Энергетик",          0.015, "🥤"),       # 1.5% шанс
}

def generate_styled_maze(width=31, height=21, loop_factor=0.2):
    """
    Генерирует лабиринт, создает циклы и автоматически спавнит предметы на полу.
    Возвращает: display_grid, maze, items_on_map
    """
    INNER_WALLS = "┌┐└┘─│┬┴├┤┼·"
    OUTER_WALLS = "╔╗╚╝═║╦╩╠╣╬·"

    if width % 2 == 0: width += 1
    if height % 2 == 0: height += 1

    maze = [[True for _ in range(width)] for _ in range(height)]

    # Алгоритм Backtracking (генератор лабиринтов)
    def carve(x, y):
        maze[y][x] = False
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 < nx < width - 1 and 0 < ny < height - 1 and maze[ny][nx]:
                maze[y + dy // 2][x + dx // 2] = False
                carve(nx, ny)

    carve(1, 1)

    # Создание циклов (удаление случайных стен)
    internal_walls = []
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if maze[y][x]:
                internal_walls.append((x, y))

    walls_to_remove_count = int(len(internal_walls) * loop_factor)
    walls_to_remove = random.sample(internal_walls, walls_to_remove_count)
    for wx, wy in walls_to_remove:
        maze[wy][wx] = False

    # Автоматическая генерация предметов на полу лабиринта
    items_on_map = {}
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if not maze[y][x]:
                if x == 1 and y == 1:
                    continue
                
                for _, (item_type, item_name, chance, icon) in LOOT_TABLE.items():
                    if random.random() < chance:
                        logical_x = x - 1
                        logical_y = y - 1
                        if item_type == "money":
                            items_on_map[(logical_x, logical_y)] = MoneyPile(
                                name=item_name, icon="₽ "
                            )
                        else:
                            items_on_map[(logical_x, logical_y)] = Loot(
                                name=item_name, icon=icon, inventory_name=item_name
                            )
                        break

    floor_positions = [
        (x - 1, y - 1)
        for y in range(1, height - 1)
        for x in range(1, width - 1)
        if not maze[y][x] and (x, y) != (1, 1)
    ]

    if len(floor_positions) < 8:
        raise ValueError("Для выхода, тайника и порталов лабиринту нужно не менее 8 свободных клеток.")

    exit_position = max(floor_positions, key=lambda position: abs(position[0]) + abs(position[1]))
    items_on_map[exit_position] = LockedExit(name="Выход", icon="🚪")

    remaining_positions = [position for position in floor_positions if position != exit_position]
    key_position = random.choice(remaining_positions)
    items_on_map[key_position] = LockedCache(
        name="Запертый тайник",
        icon="🔒",
        requirement_options=(
            ("Вилка заточенная", "Энергетик"),
            ("Отмычка",),
        ),
    )
    remaining_positions.remove(key_position)

    trap_count = max(2, len(floor_positions) // 100)
    if len(floor_positions) < trap_count + 12:
        raise ValueError("Лабиринт слишком мал для размещения всех игровых объектов.")
    feature_positions = random.sample(remaining_positions, trap_count + 4)
    for position in feature_positions[:trap_count]:
        items_on_map[position] = ScaldingPipe(
            name="Труба с кипятком", icon="🚿"
        )

    portal_positions = feature_positions[trap_count:]
    for index, (portal_id, portal_name, icon) in enumerate((
        ("blue", "Синий портал", "🔵"),
        ("purple", "Фиолетовый портал", "🟣"),
    )):
        first, second = portal_positions[index * 2:index * 2 + 2]
        items_on_map[first] = Portal(
            name=portal_name, icon=icon, pair_id=portal_id, destination=second
        )
        items_on_map[second] = Portal(
            name=portal_name, icon=icon, pair_id=portal_id, destination=first
        )

    reserved_positions = {exit_position, key_position, *feature_positions}
    support_positions = [
        position for position in floor_positions if position not in reserved_positions
    ]
    random.shuffle(support_positions)
    guaranteed_loot = (
        ("Столовая вилка", "🍴"),
        ("Техническая паста", "🧴"),
        ("Энергетик", "🥤"),
    )
    for position, (item_name, icon) in zip(support_positions[:3], guaranteed_loot):
        items_on_map[position] = Loot(
            name=item_name, icon=icon, inventory_name=item_name
        )
    for index, position in enumerate(support_positions[3:6], start=1):
        items_on_map[position] = MoneyPile(
            name=f"Запас денег #{index}", icon="₽ ", amount=50
        )

    # Построение сетки display_grid
    display_grid = [[' ' for _ in range(width)] for _ in range(height)]
    for y in range(height):
        for x in range(width):
            if not maze[y][x]:
                display_grid[y][x] = ' '
                continue
            up    = y > 0 and maze[y - 1][x]
            down  = y < height - 1 and maze[y + 1][x]
            left  = x > 0 and maze[y][x - 1]
            right = x < width - 1 and maze[y][x + 1]

            symbol = '·'
            if up and down and left and right: symbol = '┼'
            elif up and down and left:         symbol = '┤'
            elif up and down and right:        symbol = '├'
            elif up and left and right:        symbol = '┴'
            elif down and left and right:      symbol = '┬'
            elif up and down:                  symbol = '│'
            elif left and right:               symbol = '─'
            elif down and right:               symbol = '┌'
            elif down and left:                symbol = '┐'
            elif up and right:                 symbol = '└'
            elif up and left:                  symbol = '┘'
            if up or down: symbol = '│'
            elif left or right: symbol = '─'
            display_grid[y][x] = symbol

    for y in range(height):
        for x in range(width):
            if x == 0 or y == 0 or x == width - 1 or y == height - 1:
                symbol = display_grid[y][x]
                if symbol == ' ': symbol = '│'
                if symbol in INNER_WALLS:
                    idx = INNER_WALLS.index(symbol)
                    display_grid[y][x] = OUTER_WALLS[idx]
    
    return display_grid, maze, items_on_map
