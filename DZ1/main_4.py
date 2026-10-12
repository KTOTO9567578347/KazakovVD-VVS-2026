import sys
import math

class CALC():
    def __init__(self):

        def f_minus(a, b):
            return a - b
        def f_plus(a, b):
            return a + b
        def f_prod(a, b):
            return a * b
        def f_divide(a, b):
            return a / b
        def f_equals():
            print(f"Текущий результат вычислений: {self.val}")
        def f_clear():
            self.val = 0
            self.iserror = 0
            print("Память калькулятора очищена. Текущее значение: 0")
        
        self.funcs = [f_plus, f_minus, f_prod, f_divide, f_equals, f_clear]
        self.signs = ["+", '-', '*', '/', '=', "c"]
        self.non_calc = ['=', 'c']      
        self.iserror = False
        self.val = 0

    def add_operand(self, op_sign, x):
        
        if (op_sign == 'c'):
            op_f = self.funcs[self.signs.index(op_sign)]
            op_f()
            return
            
        if self.iserror:
            print(f"Действие заблокировано. Система находится в состоянии ошибки: {self.val}")
            print("Для продолжения работы введите команду 'c' (сброс).")
            return
        
        if op_sign not in self.signs:
            self.val = 'ОШИБКА: НЕВЕРНЫЙ ОПЕРАТОР!'
            self.iserror = True
            print(self.val)
            print("Допустимые знаки операций: +, -, *, /, =, c")
            return

        op_f = self.funcs[self.signs.index(op_sign)]

        try:
            if (op_sign not in self.non_calc):
                old_val = self.val
                self.val = op_f(self.val, x)
                print(f"Выполнено: {old_val} {op_sign} {x} = {self.val}")
            else:
                op_f()
            
        except ZeroDivisionError:
            self.val = "ОШИБКА: ДЕЛЕНИЕ НА 0!"
            self.iserror = True
            print(self.val)
            print("Для возобновления работы введите команду 'c' (сброс).")
            return
        
        return

print("======================================================================")
print("КАЛЬКУЛЯТОР")
print("======================================================================")
print("Руководство по эксплуатации:")
print("1. Ввод команд осуществляется накопительным итогом (исходное значение: 0).")
print("2. Формат ввода: [знак_операции] [число] (разделяются строго пробелом).")
print("3. Список поддерживаемых операций:")
print("   + (сложение)   - (вычитание)   * (умножение)   / (деление)")
print("4. Системные команды:")
print("   = (вывести итоговое значение на экран)")
print("   c (очистить память и сбросить состояние ошибки)")
print("\nПримеры корректного ввода данных:")
print("   + 12.5       (прибавить к текущему значению 12.5)")
print("   * 2          (умножить текущее значение на 2)")
print("   =            (вывести результат на экран)")
print("   c            (сбросить все вычисления в 0)")
print("======================================================================")
print("Программа готова к работе. Пожалуйста, введите первую команду:")

calculator = CALC()

while True:
    try:
        user_input = input("Ввод команды -> ").strip()
        if not user_input:
            continue
            
        cmd = user_input.split()
        op, x = "+", 0

        if len(cmd) == 1:
            op = cmd[0]
        elif len(cmd) == 2:
            op = cmd[0]
            try:
                x = float(cmd[1])
            except ValueError:
                print("Ошибка ввода: Вторым аргументом должно выступать число (например: 5 или 2.5).")
                continue
        else:
            print("Команда не распознана. Используйте формат: 'оператор число' или 'оператор'.")
            continue

        calculator.add_operand(op, x)
        
    except (KeyboardInterrupt, EOFError):
        print("\nПрограмма успешно завершила свою работу.")
        break
