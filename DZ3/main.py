import os
import readchar
from mazegen import generate_styled_maze
from maze import Maze
from characters import Player, Monster

display_grid, grid_matrix, items_on_map = generate_styled_maze(29, 29, loop_factor=0.2)
maze = Maze(grid=grid_matrix, displayable=display_grid)

# Персонажи
player = Player(start_x=0, start_y=0, maze=maze)

p1_x, p1_y = maze.get_random_empty_position()
police_1 = Monster(start_x=p1_x, start_y=p1_y, maze=maze)

p2_x, p2_y = maze.get_random_empty_position()
police_2 = Monster(start_x=p2_x, start_y=p2_y, maze=maze)

all_entities = [player, police_1, police_2]
monsters = [police_1, police_2]

BRIBE_COST = 100

while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    GREATING_TEXT = "🏢 ПОБЕГ ИЗ ПОДВАЛОВ НИТУ МИСИС 🏢"
    print("╔"+(len(GREATING_TEXT)+4)*"═"+"╗")
    print("║ " + GREATING_TEXT + " ║")
    print("╚"+(len(GREATING_TEXT)+4)*"═"+"╝")

    print(f"❤️ HP: [{player.hp}/{player.max_hp}]  |  ₽ ДЕНЬГИ: {player.money}₽")
    print(f"🎒 ИНВЕНТАРЬ: {', '.join(player.inventory) if player.inventory else 'Пусто'}")
    print("-" * 40)
    
    # Отрисовка
    maze.display(active_player=player, characters=all_entities, items_on_map=items_on_map, vision_radius=4, fog_of_war=True)
    print("Управление: W,A,S,D | E - взаимодействие | T - команды | Ctrl+C - выход")
    
    try:
        user_step = readchar.readkey().lower()
    except KeyboardInterrupt:
        break

    if user_step == 't':
        raw_command = input("\n[КОНСОЛЬ] Введите команду: ")
        
        # Передача выполнения внутрь игрока
        player.execute_command(raw_command)
        
        input("\nНажмите Enter, чтобы вернуться к игре...")

    
    player.update(user_step, items_on_map)
    if player.game_won:
        print("🎉 Победа! Вы покинули лабиринт.")
        break
    if not player.is_alive:
        print("💀 Здоровье закончилось. Игра окончена.")
        break

    for monster in monsters:
        monster.update(player.x, player.y)
        
    # Проверка встречи с монстром
    game_over = False
    for monster in monsters:
        if player.x == monster.x and player.y == monster.y:
            if player.money >= BRIBE_COST:
                player.money -= BRIBE_COST
                print(f"\n Задобрил охрану за {BRIBE_COST}₽.")
                monster.x, monster.y = maze.get_random_empty_position()
                input("Нажмите Enter для продолжения...")
            else:
                player.inventory.clear()
                player.money = 0
                os.system('cls' if os.name == 'nt' else 'clear')
                print(" Охрана кампуса поймала вас. Побег не удался.")
                game_over = True
                break
                
    if game_over:
        break
