import inspect

class level:
    def print_method_menu(self):
        print("\nВыберите номер метода:")
        for i, cmd in enumerate(self.descr_list):
            print(f"({i}) {cmd}")

    def __init__(self, f_list, descr_list):
        self.f_list = f_list
        self.descr_list = descr_list

    def opis(self):
        print("\nУровень умеет: ")
        print(*self.descr_list, sep = '\n')

    def make_test(self, inp_args):
        print(f"\nТЕСТИРОВАНИЕ. Применение к тестовым данным методов:")
        for i, (descr, func) in enumerate(zip(self.descr_list, self.f_list)):
            print(f"\nМетод {i}: {descr}")
            
            datasets = inp_args[i] 
            
            for dataset in datasets:
                try:
                    result = func(**dataset)
                    print(f"  -> При параметрах {list(dataset.values())}, Результат: {result}")
                except Exception as e:
                    print(f"  -> При параметрах {list(dataset.values())}, Ошибка: {e}")
                    
        print("\nТестирование завершено.\n")

    def run(self, test_args):
        print("OK")
        self.opis()
        self.make_test(test_args)
        
        is_cont = input("ПРОДОЛЖИТЬ? [Y = ДА, иначе нет]: ") == 'Y'

        if is_cont:
            self.print_method_menu()
            method_num = int(input("ВВЕДИТЕ НОМЕР МЕТОДА ИЗ ДОСТУПНЫХ: "))            
            chosen_func = self.f_list[method_num]
            sig = inspect.signature(chosen_func)
            arg_names = list(sig.parameters.keys())
            user_args = {}
            print(f"\nДля работы метода требуются аргументы {arg_names}:")
            for arg in arg_names:
                user_args[arg] = input(f"Введите значение для '{arg}': ")            
            try:
                result = chosen_func(**user_args)
                print(f"\nРЕЗУЛЬТАТ: {result}")
            except Exception as e:
                print(f"\nОшибка при выполнении: {e}")
        else:
            return

LEVELS = [
    # УРОВЕНЬ 1
    level(
        f_list=[
             lambda text: text.upper(),
             lambda text: text.lower(),
             lambda text: text.capitalize(),
        ],
        descr_list = [
           "в верхний регистр .upper()",
           "в нижний регистр .lower()",
           "в правильное написание, большая буква после пробела .capitalize()",
        ]
    ),

    # УРОВЕНЬ 2
    level(
        f_list=[
             lambda text, val: text.find(val),
             lambda text, oldval, newval: text.replace(oldval, newval),
             lambda text, val: text.count(val),
             lambda text, val: text.index(val),
        ],
        descr_list = [
           "Найти val в text. Аргументы: <text, val>.",
           "Заменить вхождение oldval в text на newval. Аргументы: <text, oldval, newval>.",
           "Посчитать все val в text. Аргументы: <text, val>.",
           "Найти первое вхождение val в text (ошибка если не найдёт). Аргументы: <text, val>.",
        ]
    ),

    # УРОВЕНЬ 3
    level(
            f_list=[
                 lambda text, sep: text.split(sep),
                 lambda vallist, sep: sep.join(vallist.split(' ')),
            ],
            descr_list = [
               "Разбить text в список по sep. Аргументы: <text, sep>.",
               "Соединить vallist в текст через sep. Аргументы: <vallist, sep>. #vallist - через пробел",
            ]
    ),

    # УРОВЕНЬ 4
    level(
            f_list=[
                lambda text: text.isdigit(),
                lambda text, valslist: text.strip(valslist),
                lambda text: text.isalpha(),
                lambda text, fargs: text.format(fargs),
            ],
            descr_list = [
                "Является ли text числом. Аргументы: <text>.",
                "Удалить все знаки из строки vallist из начала и конца text. Аргументы: <text, valslist>. #valslist - без пробелов, строка знаков.",
                "Является ли text набором букв. Аргументы: <text>.",
                "Форматиовать text в формат fargs. . Аргументы: <text, fargs>. #как писать fargs и text - смотрите в доках питона" ,
            ]
    ),

    # УРОВЕНЬ 5
    level(
        f_list=[
            lambda text: ' '.join(str(text).strip().capitalize().replace(';', ' ').split(sep = ' ')),
        ],
        descr_list=[
            'Сделать текст человекочитаемым. Аргументы: <text>.',
        ]
    )
]

test_args = [
    [  #ТЕСТ1
        [{"text": "пРиВет МИР"}], 
        [{"text": "пРиВет МИР"}], 
        [{"text": "пРиВет МИР"}]
    ], 
    
    [#ТЕСТ2
        [{"text": "Ботать это круто", "val": "круто"},],
        [{"text": "Ботать это круто", "oldval": "круто", "newval": "@"}],
        [{"text": "Ботать это круто", "val": "о"}],
        [{"text": "Ботать это круто", "val": "т"}],
    ],
    [#ТЕСТ3
        [{"text": "1,2,3,4", "sep":","}],
        [{"vallist": "1 2 3 4", "sep":","}],
    ],
    [#ТЕСТ4
        [{"text": "1234*&%1$"}, {"text": "    abc1234   "}],
        [{"text": "1234*&%1$", "valslist": " "}, {"text": "    abc1234   ", "valslist": " "}],
        [{"text": "1234*&%1$"}, {"text": "    abc1234   "}],
        [{"text": "1234*&%1$", "fargs":"NONE"}, {"text": "    abc1234   ", "fargs":"NONE"}],
    ],
    [#ТЕСТ5
        [{"text": "        pYtHon;is;AWESome    "}],
    ]
]

print("Приветствие.")
valid_levels = list(range(1, len(LEVELS)+1))
print("Уровни: ", valid_levels)

lnum = int(input("ВВЕДИТЕ УРОВЕНЬ ИЗ ДОСТУПНЫХ: "))
if lnum in valid_levels:
    LEVELS[lnum-1].run(test_args[lnum-1])
else:
    print("Неверный уровень!")
