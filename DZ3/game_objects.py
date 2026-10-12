from dataclasses import dataclass


@dataclass
class GameObject:
    name: str
    icon: str

    def interact(self, player) -> bool:
        return False

    def enter(self, player) -> None:
        pass


@dataclass
class Loot(GameObject):
    inventory_name: str

    def interact(self, player) -> bool:
        player.inventory.append(self.inventory_name)
        print(f"В инвентарь добавлено: {self.inventory_name}")
        return True


@dataclass
class MoneyPile(GameObject):
    amount: int = 50

    def interact(self, player) -> bool:
        player.money += self.amount
        print(f"Подобрано: {self.name} (+{self.amount}₽)")
        return True


@dataclass
class LockedCache(GameObject):
    requirement_options: tuple[tuple[str, ...], ...]
    reward: str = "Ключ от выхода"

    def interact(self, player) -> bool:
        available = next(
            (
                requirements
                for requirements in self.requirement_options
                if all(item in player.inventory for item in requirements)
            ),
            None,
        )
        if available is None:
            options = " или ".join(
                " + ".join(f"«{item}»" for item in requirements)
                for requirements in self.requirement_options
            )
            print(f"🔒 Тайник заперт. Нужны предметы: {options}.")
            print("💡 Подсказка: осмотрите лут и используйте команду crafts, чтобы узнать рецепты.")
            return False

        for item in available:
            player.inventory.remove(item)
        player.inventory.append(self.reward)
        print(f"🔑 Тайник открыт. Получен предмет: {self.reward}.")
        return True


@dataclass
class LockedExit(GameObject):
    key_name: str = "Ключ от выхода"

    def interact(self, player) -> bool:
        if self.key_name not in player.inventory:
            print("🔒 Выход закрыт. Откройте запертый тайник и возьмите ключ.")
            print("💡 Полный порядок прохождения: команда guide.")
            return False
        player.inventory.remove(self.key_name)
        player.game_won = True
        print("🚪 Выход открыт! Вы выбрались из лабиринта.")
        return True


@dataclass
class ScaldingPipe(GameObject):
    damage: int = 25
    protective_item: str = "Жилет электрика"

    def enter(self, player) -> None:
        if self.protective_item in player.inventory:
            player.inventory.remove(self.protective_item)
            print("🦺 Жилет электрика защитил от кипятка и сгорел.")
            return

        player.hp = max(0, player.hp - self.damage)
        player.is_alive = player.hp > 0
        print(f"🚿 Труба ошпарила кипятком! Здоровье: {player.hp}/{player.max_hp}.")


@dataclass
class Portal(GameObject):
    pair_id: str
    destination: tuple[int, int] | None = None

    def enter(self, player) -> None:
        if self.destination is None:
            raise ValueError(f"Для портала «{self.name}» не найдена парная точка.")
        player.x, player.y = self.destination
        print(f"🌀 Портал переместил вас в точку {self.destination}.")
