from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class Recipe:
    name: str
    ingredients: tuple[str, ...]
    result: str
    cost: int
    description: str


class RecipeBook:
    def __init__(self, recipes: tuple[Recipe, ...]):
        self.recipes = {recipe.name: recipe for recipe in recipes}

    def describe(self) -> None:
        print("🔧 РЕЦЕПТЫ:")
        for recipe in self.recipes.values():
            ingredients = " + ".join(recipe.ingredients)
            print(f"  {recipe.name}: {ingredients} → {recipe.result} ({recipe.cost}₽)")
            print(f"    {recipe.description}")

    def craft(self, player, requested_name: str) -> bool:
        recipe = self.recipes.get(requested_name.casefold())
        if recipe is None:
            print(f"❌ Рецепт «{requested_name}» не найден. Введите crafts.")
            return False

        required = Counter(recipe.ingredients)
        available = Counter(player.inventory)
        missing = [
            f"{item} ×{count - available[item]}"
            for item, count in required.items()
            if available[item] < count
        ]
        if missing:
            print(f"❌ Не хватает ингредиентов: {', '.join(missing)}.")
            return False
        if player.money < recipe.cost:
            print(f"❌ Для крафта нужно {recipe.cost}₽, у вас {player.money}₽.")
            return False

        for item, count in required.items():
            for _ in range(count):
                player.inventory.remove(item)
        player.money -= recipe.cost
        player.inventory.append(recipe.result)
        print(f"🔧 Создано: {recipe.result}. {recipe.description}")
        return True


RECIPES = RecipeBook(
    (
        Recipe(
            "fork",
            ("Столовая вилка", "Техническая паста"),
            "Вилка заточенная",
            25,
            "Нужна для открытия тайника.",
        ),
        Recipe(
            "lockpick",
            ("Столовая вилка", "Энергетик"),
            "Отмычка",
            15,
            "Альтернативный способ открыть тайник.",
        ),
        Recipe(
            "medkit",
            ("Техническая паста", "Энергетик"),
            "Аптечка",
            20,
            "Команда use аптечка восстанавливает до 40 HP.",
        ),
        Recipe(
            "vest",
            ("Техническая паста", "Столовая вилка"),
            "Жилет электрика",
            30,
            "Защищает от одной трубы с кипятком.",
        ),
    )
)
