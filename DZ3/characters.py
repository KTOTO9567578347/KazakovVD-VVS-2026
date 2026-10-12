from abc import ABC, abstractmethod
from maze import Maze
import argparse
import shlex
import ast
import math
import operator
from crafting import RECIPES
from game_objects import GameObject, Portal


class _InventoryExpressionEvaluator:
    """Функционал проверки корректности и безопасности выражений, вводимых пользователем в качестве генератора списков"""

    MAX_NODES = 200
    MAX_EXPRESSION_LENGTH = 2_000
    MAX_ITERATIONS = 10_000
    MAX_RESULTS = 1_000
    MAX_STRING_LENGTH = 10_000
    MAX_INTEGER_BITS = 4_096

    # Операторы с двумя и одним операндами (на случай расчётов в числах)
    _binary_operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    }
    
    _unary_operators = {
        ast.Not: operator.not_,
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
        ast.Invert: operator.invert,
    }

    # Сравнение строк и чисел
    _comparisons = {
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        ast.In: lambda left, right: left in right,
        ast.NotIn: lambda left, right: left not in right,
    }

    # Набор функций для безопасных генераторов
    _functions = {
        "abs": abs,
        "all": all,
        "any": any,
        "bool": bool,
        "float": float,
        "int": int,
        "len": len,
        "max": max,
        "min": min,
        "round": round,
        "sorted": sorted,
        "str": str,
        "sum": sum,
        "lower": lambda s: str(s).lower(),
        "upper": lambda s: str(s).upper(),
        "capitalize": lambda s: str(s).capitalize(),
        "title": lambda s: str(s).title(),
        "swapcase": lambda s: str(s).swapcase(),
        "strip": lambda s, chars=None: str(s).strip(chars),
        "lstrip": lambda s, chars=None: str(s).lstrip(chars),
        "rstrip": lambda s, chars=None: str(s).rstrip(chars),
        "replace": lambda s, old, new, count=-1: str(s).replace(str(old), str(new), count),
        "count": lambda s, sub: str(s).count(str(sub)),
        "find": lambda s, sub: str(s).find(str(sub)),
        "isdigit": lambda s: str(s).isdigit(),
        "isalpha": lambda s: str(s).isalpha(),
        "isalnum": lambda s: str(s).isalnum(),
        "islower": lambda s: str(s).islower(),
        "isupper": lambda s: str(s).isupper(),
        "startswith": lambda s, prefix: str(s).startswith(str(prefix)),
        "endswith": lambda s, suffix: str(s).endswith(str(suffix)),
    }

    def __init__(self, inventory: list[str]):
        if len(inventory) > self.MAX_RESULTS:
            raise ValueError("Инвентарь слишком велик для безопасного вычисления.")
        self.inventory = list(inventory)
        self.iterations = 0

    def evaluate(self, expression: str):
        if len(expression) > self.MAX_EXPRESSION_LENGTH:
            raise ValueError("Выражение слишком длинное.")

        # Дерево выражения
        tree = ast.parse(expression, mode="eval")
        if sum(1 for _ in ast.walk(tree)) > self.MAX_NODES:
            raise ValueError("Выражение слишком сложное.")
        if not isinstance(tree.body, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            raise ValueError("Разрешены только генераторы списков, множеств, словарей и выражений.")
        if not tree.body.generators or not isinstance(tree.body.generators[0].iter, ast.Name) or tree.body.generators[0].iter.id != "items":
            raise ValueError("Первый цикл генератора должен перебирать список 'items'.")
        return self._evaluate(tree.body, {})

    def _checked(self, value):
        if isinstance(value, str) and len(value) > self.MAX_STRING_LENGTH:
            raise ValueError("Результирующая строка слишком длинная.")
        if isinstance(value, int) and value.bit_length() > self.MAX_INTEGER_BITS:
            raise ValueError("Результирующее число слишком велико.")
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("Недопустимое числовое значение.")
        if isinstance(value, (list, tuple, set, dict)) and len(value) > self.MAX_RESULTS:
            raise ValueError("Слишком большой результат.")
        return value

    def _evaluate(self, node, scope: dict[str, object]):
        if isinstance(node, ast.Constant):
            if not isinstance(node.value, (str, int, float, bool, type(None))):
                raise ValueError("Этот тип констант запрещён.")
            return self._checked(node.value)

        if isinstance(node, ast.Name):
            if node.id == "items":
                return self.inventory
            if node.id in scope:
                return scope[node.id]
            if node.id in self._functions:
                return self._functions[node.id]
            raise ValueError(f"Имя '{node.id}' не разрешено.")

        if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            values = [self._evaluate(element, scope) for element in node.elts]
            if isinstance(node, ast.List):
                return self._checked(values)
            if isinstance(node, ast.Tuple):
                return self._checked(tuple(values))
            return self._checked(set(values))

        if isinstance(node, ast.Dict):
            if any(key is None for key in node.keys):
                raise ValueError("Распаковка словарей запрещена.")
            result = {
                self._evaluate(key, scope): self._evaluate(value, scope)
                for key, value in zip(node.keys, node.values)
            }
            return self._checked(result)

        if isinstance(node, ast.BinOp):
            operation = self._binary_operators.get(type(node.op))
            if operation is None:
                raise ValueError("Этот арифметический оператор запрещён.")
            left = self._evaluate(node.left, scope)
            right = self._evaluate(node.right, scope)
            if isinstance(node.op, ast.Mult):
                if (
                    isinstance(left, (str, list, tuple))
                    and isinstance(right, int)
                    and len(left) * max(right, 0) > self.MAX_STRING_LENGTH
                ):
                    raise ValueError("Результирующее значение слишком велико.")
                if (
                    isinstance(right, (str, list, tuple))
                    and isinstance(left, int)
                    and len(right) * max(left, 0) > self.MAX_STRING_LENGTH
                ):
                    raise ValueError("Результирующее значение слишком велико.")
            return self._checked(operation(left, right))

        if isinstance(node, ast.UnaryOp):
            operation = self._unary_operators.get(type(node.op))
            if operation is None:
                raise ValueError("Этот унарный оператор запрещён.")
            return self._checked(operation(self._evaluate(node.operand, scope)))

        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                result = True
                for value in node.values:
                    result = self._evaluate(value, scope)
                    if not result:
                        break
                return result
            if isinstance(node.op, ast.Or):
                result = False
                for value in node.values:
                    result = self._evaluate(value, scope)
                    if result:
                        break
                return result
            raise ValueError("Этот логический оператор запрещён.")

        if isinstance(node, ast.Compare):
            left = self._evaluate(node.left, scope)
            for operation_node, comparator in zip(node.ops, node.comparators):
                operation = self._comparisons.get(type(operation_node))
                if operation is None:
                    raise ValueError("Это сравнение запрещено.")
                right = self._evaluate(comparator, scope)
                if not operation(left, right):
                    return False
                left = right
            return True

        if isinstance(node, ast.IfExp):
            branch = node.body if self._evaluate(node.test, scope) else node.orelse
            return self._evaluate(branch, scope)

        if isinstance(node, ast.Subscript):
            value = self._evaluate(node.value, scope)
            if not isinstance(value, (str, list, tuple, dict)):
                raise ValueError("Индексация этого типа запрещена.")
            index = self._evaluate(node.slice, scope)
            return self._checked(value[index])

        if isinstance(node, ast.Slice):
            parts = [
                self._evaluate(part, scope) if part is not None else None
                for part in (node.lower, node.upper, node.step)
            ]
            if any(part is not None and not isinstance(part, int) for part in parts):
                raise ValueError("Индексы среза должны быть целыми числами.")
            return slice(*parts)

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in self._functions:
                raise ValueError("Разрешены только безопасные встроенные функции.")
            if node.keywords or any(isinstance(arg, ast.Starred) for arg in node.args):
                raise ValueError("Распаковка аргументов функций запрещена.")
            args = [self._evaluate(arg, scope) for arg in node.args]
            return self._checked(self._functions[node.func.id](*args))

        if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            values = []

            def visit_generator(index: int, current_scope: dict[str, object]):
                if index == len(node.generators):
                    if len(values) >= self.MAX_RESULTS:
                        raise ValueError("Слишком много результатов.")
                    if isinstance(node, ast.DictComp):
                        key = self._evaluate(node.key, current_scope)
                        value = self._evaluate(node.value, current_scope)
                        values.append((key, value))
                    else:
                        values.append(self._evaluate(node.elt, current_scope))
                    return

                generator = node.generators[index]
                if generator.is_async:
                    raise ValueError("Асинхронные генераторы запрещены.")
                iterable = self._evaluate(generator.iter, current_scope)
                if not isinstance(iterable, (list, tuple, str, dict, set)):
                    raise ValueError("Этот источник данных нельзя перебирать.")
                for item in iterable:
                    self.iterations += 1
                    if self.iterations > self.MAX_ITERATIONS:
                        raise ValueError("Превышен лимит итераций.")
                    nested_scope = dict(current_scope)
                    self._bind_target(generator.target, item, nested_scope)
                    if all(self._evaluate(condition, nested_scope) for condition in generator.ifs):
                        visit_generator(index + 1, nested_scope)

            visit_generator(0, scope)
            if isinstance(node, ast.DictComp):
                return self._checked(dict(values))
            if isinstance(node, ast.SetComp):
                return self._checked(set(values))
            return self._checked(values)

        raise ValueError(f"Конструкция {type(node).__name__} запрещена.")

    def _bind_target(self, target, value, scope: dict[str, object]):
        if isinstance(target, ast.Name):
            if target.id.startswith("_") or target.id == "items":
                raise ValueError("Это имя нельзя использовать в генераторе.")
            scope[target.id] = self._checked(value)
            return
        if isinstance(target, (ast.Tuple, ast.List)):
            if not isinstance(value, (tuple, list)) or len(target.elts) != len(value):
                raise ValueError("Значение не соответствует распаковке генератора.")
            for element, item in zip(target.elts, value):
                self._bind_target(element, item, scope)
            return
        raise ValueError("Этот тип переменной цикла запрещён.")

class Character(ABC):
    def __init__(self, start_x: int, start_y: int, maze: Maze, icon: str, hp: int = 100):
        """Базовый класс с поддержкой здоровья и иконки."""
        self.x = start_x
        self.y = start_y
        self.maze = maze
        self.icon = icon
        self.hp = hp
        self.max_hp = hp
        self.is_alive = True

    def move(self, direction: str) -> bool:
        """Логика перемещения (без изменений)."""
        new_x, new_y = self.x, self.y
        direction_lower = direction.lower()
        
        if direction_lower == 'w':    new_y -= 1
        elif direction_lower == 's':  new_y += 1
        elif direction_lower == 'a':  new_x -= 1
        elif direction_lower == 'd':  new_x += 1
        else: return False

        if not self.maze.is_wall(new_x, new_y):
            self.x = new_x
            self.y = new_y
            return True
        return False

    @abstractmethod
    def update(self, *args, **kwargs):
        pass


class Player(Character):
    SAVE_COST_PER_ITEM = 10
    TRAP_DAMAGE = 25
    HEALING_AMOUNT = 40

    def __init__(self, start_x: int, start_y: int, maze: Maze):
        super().__init__(start_x, start_y, maze, icon="👨", hp=100)
        self.money = 0            # Шкала денег
        self.inventory = []       # Массив под инвентарь
        self.copied_inventory: list[str] = []
        self.last_inventory_slice: list[str] = []
        self.saved_inventories: list[list[str]] = []
        self.game_won = False

    def execute_command(self, raw_input: str):
        """Парсит строку с учетом кавычек и вызывает нужный метод."""
        raw_input = raw_input.strip()
        if not raw_input:
            return
        try:
            args_list = shlex.split(raw_input)
        except ValueError as e:
            print(f"❌ Ошибка синтаксиса (проверьте кавычки): {e}")
            return

        cmd_name = args_list[0].lower()
        cmd_args = args_list[1:]

        method = getattr(self, f"cmd_{cmd_name}", None)
        if method and callable(method):
            method(cmd_args)
        else:
            print(
                f"❌ Неизвестная команда. Введите 'help' для списка команд."
            )

    # КОМАНДЫ ТЕРМИНАЛА

    def cmd_help(self, _args: list[str]):
        """Выводит список всех доступных команд и их синтаксис."""
        print("\n📜 СПИСОК ДОСТУПНЫХ КОМАНД:")
        print("-" * 60)
        for attr_name in sorted(dir(self)):
            if not attr_name.startswith("cmd_"):
                continue
            method = getattr(self, attr_name)
            clean_name = attr_name[4:]
            if hasattr(method, "parser"):
                parser: argparse.ArgumentParser = method.parser
                usage = parser.format_usage().replace("usage: ", "").strip()
                print(f"  {usage:<25} - {parser.description}")
                continue
            description = method.__doc__.split("\n")[0] if method.__doc__ else "Нет описания."
            print(f"  {clean_name:<25} - {description}")
        print("-" * 60)
        print("Операции с коробкой: append, extend, remove, pop, sort, reverse, copy, slice.")
        print("Подробное прохождение: guide | все рецепты: crafts")

    def cmd_guide(self, _args: list[str]):
        """Показывает порядок прохождения лабиринта и предметы для тайника."""
        print(
            "\n🧭 ПОБЕГ ИЗ ПОДВАЛОВ НИТУ МИСИС:\n"
            "1. Ищите припасы в коридорах и подбирайте их клавишей E.\n"
            "2. Соберите «Столовая вилка», «Техническая паста» и «Энергетик».\n"
            "3. Откройте тайник одним из способов:\n"
            "   • craft lockpick — вилка + «Энергетик», затем E у тайника;\n"
            "   • craft fork — вилка + паста, затем заточенная вилка + «Энергетик».\n"
            "4. Тайник выдаст ключ. Найдите 🚪 и нажмите E.\n"
            "5. Жилет электрика защищает от одной трубы с кипятком; порталы переносят "
            "к парному кругу.\n"
            "Собирайте деньги и применяйте аптечку командой use аптечка."
        )

    def cmd_crafts(self, _args: list[str]):
        """Показывает все рецепты, ингредиенты, цены и эффекты."""
        RECIPES.describe()

    def cmd_append(self, args: list[str]):
        """Кладёт один предмет в коробку: append название предмета."""
        item_name = " ".join(args).strip()
        if not item_name:
            print("❌ Укажите предмет: append название предмета.")
            return
        self.inventory.append(item_name)
        print(f"📦 В коробку добавлен один предмет: {item_name}.")

    def cmd_extend(self, args: list[str]):
        """Кладёт несколько предметов в коробку: extend \"предмет 1\" предмет2."""
        if not args:
            print("❌ Перечислите предметы: extend \"предмет 1\" предмет2.")
            return
        self.inventory.extend(args)
        print(f"📦 В коробку добавлено предметов: {len(args)}.")

    def cmd_copy(self, _args: list[str]):
        """Создаёт отдельную копию списка предметов, не меняя оригинал."""
        self.copied_inventory = self.inventory.copy()
        print(f"📋 Копия коробки: {self.copied_inventory}")

    def cmd_slice(self, args: list[str]):
        """Показывает и сохраняет отдельный срез: slice start:stop[:step]."""
        if len(args) > 1:
            print("❌ Использование: slice start:stop[:step].")
            return
        if not args:
            start, stop, step = None, None, None
        else:
            parts = args[0].split(":")
            if len(parts) not in {2, 3}:
                print("❌ Срез задаётся как start:stop[:step], например slice 1:5:2.")
                return
            try:
                indices = [int(part) if part else None for part in parts]
            except ValueError:
                print("❌ Индексы среза должны быть целыми числами.")
                return
            start, stop = indices[:2]
            step = indices[2] if len(indices) == 3 else None
            if step == 0:
                print("❌ Шаг среза не может быть равен нулю.")
                return
        self.last_inventory_slice = self.inventory[slice(start, stop, step)]
        print(f"🔎 Срез коробки: {self.last_inventory_slice}")

    def cmd_remove(self, args: list[str]):
        """Удаляет предмет по его названию."""
        parser = argparse.ArgumentParser(
            prog="remove", description="Удаляет предмет из инвентаря."
        )
        parser.add_argument(
            "name", type=str, nargs="+", help="Название предмета"
        )

        try:
            parsed = parser.parse_args(args)
        except SystemExit:
            return

        item_name = " ".join(parsed.name)

        for item in self.inventory:
            if item.lower() == item_name.lower():
                self.inventory.remove(item)
                print(f"🗑️ '{item}' удален из инвентаря.")
                return
        print(f"❌ Предмет '{item_name}' не найден.")

    cmd_remove.parser = argparse.ArgumentParser(
        prog="remove", description="Удаляет предмет по названию."
    )
    cmd_remove.parser.add_argument("item_name", help="Имя предмета")

    def cmd_pop(self, args: list[str]):
        """Удаляет предмет по индексу."""
        parser = argparse.ArgumentParser(
            prog="pop", description="Удаляет предмет по индексу."
        )

        parser.add_argument(
            "index",
            type=int,
            nargs="?",
            default=-1,
            help="Индекс элемента (по умолчанию последний)",
        )

        try:
            parsed = parser.parse_args(args)
        except SystemExit:
            return

        try:
            removed = self.inventory.pop(parsed.index)
            print(f"🗑️ Выброшен предмет: '{removed}' [индекс {parsed.index}].")
        except IndexError:
            print("❌ Ошибка: Неверный индекс или инвентарь пуст.")

    cmd_pop.parser = argparse.ArgumentParser(
        prog="pop", description="Удаляет предмет по индексу."
    )
    cmd_pop.parser.add_argument(
        "[index]", type=int, nargs="?", help="Индекс (опционально)"
    )

    def cmd_sort(self, _args: list[str]):
        """Сортирует инвентарь."""
        self.inventory.sort()
        print("🎒 Инвентарь отсортирован по алфавиту.")

    def cmd_reverse(self, _args: list[str]):
        """Переворачивает инвентарь."""
        self.inventory.reverse()
        print("🎒 Инвентарь перевёрнут.")

    def cmd_in(self, args: list[str]):
        """Проверяет наличие предмета."""
        item_name = " ".join(args)
        if not item_name:
            print("❌ Укажите название предмета.")
            return

        has_item = any(item.lower() == item_name.lower() for item in self.inventory)
        print(
            f"{'✅ Есть' if has_item else '❌ Нет'} в инвентаре: '{item_name}'."
        )

    def cmd_index(self, args: list[str]):
        """Ищет индекс предмета."""
        item_name = " ".join(args)
        if not item_name:
            print("❌ Укажите название предмета.")
            return

        try:
            found = [i.lower() for i in self.inventory].index(item_name.lower())
            print(
                f"🔍 Предмет '{self.inventory[found]}' найден по индексу: {found}"
            )
        except ValueError:
            print(f"❌ Предмет '{item_name}' не найден.")

    def cmd_save(self, args: list[str]):
        """Сохраняет весь инвентарь или срез за 10₽ за предмет: save [start:end]."""
        if len(args) > 1:
            print("❌ Использование: save [start:end]")
            return

        if not args:
            snapshot = list(self.inventory)
        else:
            try:
                start_text, separator, stop_text = args[0].partition(":")
                if not separator or ":" in stop_text:
                    raise ValueError
                start = int(start_text) if start_text else None
                stop = int(stop_text) if stop_text else None
                snapshot = list(self.inventory[slice(start, stop)])
            except ValueError:
                print("❌ Срез задаётся как start:end, например save 1:4.")
                return

        cost = len(snapshot) * self.SAVE_COST_PER_ITEM
        if self.money < cost:
            print(f"❌ Недостаточно денег: нужно {cost}₽, у вас {self.money}₽.")
            return

        self.money -= cost
        self.saved_inventories.append(snapshot)
        print(f"💾 Сохранён снимок #{len(self.saved_inventories)}: {len(snapshot)} предметов, цена {cost}₽.")

    def cmd_saves(self, _args: list[str]):
        """Показывает сохранённые снимки инвентаря."""
        if not self.saved_inventories:
            print("💾 Сохранённых снимков пока нет.")
            return
        for index, snapshot in enumerate(self.saved_inventories, start=1):
            items = ", ".join(snapshot) if snapshot else "Пусто"
            print(f"💾 #{index}: [{items}]")

    def cmd_craft(self, args: list[str]):
        """Создаёт предмет по рецепту: craft fork|lockpick|medkit."""
        if not args:
            self.cmd_crafts([])
            return
        requested_name = " ".join(args).strip().casefold()
        aliases = {
            "вилка": "fork",
            "заточка": "fork",
            "отмычка": "lockpick",
            "аптечка": "medkit",
            "жилет": "vest",
        }
        RECIPES.craft(self, aliases.get(requested_name, requested_name))

    def cmd_use(self, args: list[str]):
        """Использует предмет: use аптечка восстанавливает до 40 HP."""
        item_name = " ".join(args).strip().casefold()
        if item_name not in {"аптечка", "medkit"}:
            print("❌ Можно использовать аптечку: use аптечка.")
            return

        if "Аптечка" not in self.inventory:
            print("❌ В инвентаре нет аптечки.")
            return
        if self.hp >= self.max_hp:
            print("❤️ Здоровье уже полное; аптечка сохранена.")
            return
        self.inventory.remove("Аптечка")
        self.hp = min(self.max_hp, self.hp + self.HEALING_AMOUNT)
        self.is_alive = self.hp > 0
        print(f"❤️ Аптечка восстановила здоровье: {self.hp}/{self.max_hp}.")

    def cmd_eval(self, args: list[str]):
        """Безопасно применяет генератор над 'items' (список инвентаря)."""
        expr = " ".join(args)
        if not expr:
            print("❌ Введите выражение для eval.")
            return

        try:
            result = _InventoryExpressionEvaluator(self.inventory).evaluate(expr)
            if isinstance(result, set):
                result = sorted(result, key=repr)
            print(f"⚙️ Результат:\n{result}")
        except SyntaxError as e:
            print(f"❌ Ошибка в синтаксисе Python: {e.msg}")
        except RecursionError:
            print("❌ Ошибка выполнения: выражение слишком глубоко вложено.")
        except (ArithmeticError, TypeError, ValueError, KeyError, IndexError) as e:
            print(f"❌ Ошибка выполнения: {e}")

    def update(self, key_pressed: str, items_on_map: dict):
        """Перемещает игрока и передаёт события объекту на клетке."""
        if not self.is_alive:
            return

        old_position = (self.x, self.y)
        if key_pressed in {"w", "a", "s", "d"}:
            self.move(key_pressed)
        position = (self.x, self.y)
        game_object = items_on_map.get(position)
        if not isinstance(game_object, GameObject):
            return

        if key_pressed == "e":
            if game_object.interact(self):
                del items_on_map[position]
            elif isinstance(game_object, Portal):
                print("🌀 Войдите на портал шагом, чтобы переместиться.")
            return

        if key_pressed in {"w", "a", "s", "d"} and position != old_position:
            game_object.enter(self)


class Monster(Character):
    """Охранник, патрулирующий подвальные коридоры."""

    def __init__(self, start_x: int, start_y: int, maze: Maze):
        super().__init__(start_x, start_y, maze, icon="👮", hp=100)

    def update(self, player_x: int, player_y: int):
        import random
        directions = []
        if self.x < player_x: directions.append('d')
        elif self.x > player_x: directions.append('a')
        if self.y < player_y: directions.append('s')
        elif self.y > player_y: directions.append('w')
        random.shuffle(directions)
        moved = False
        for d in directions:
            if self.move(d):
                moved = True
                break
        if not moved:
            all_p = ['w', 's', 'a', 'd']
            random.shuffle(all_p)
            for d in all_p:
                if self.move(d): break
