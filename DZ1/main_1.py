a = float(input("ВВЕДИТЕ ОПЕРАНД 1:   "))
op = input('ВВЕДИТЕ ОПЕРАЦИЮ [ОДИН ИЗ: +,-,*,/]:   ')
b = float(input("ВВЕДИТЕ ОПЕРАНД 2:   "))

print("РЕЗУЛЬТАТ ОПЕРАЦИ:   ")
oplist = ['+', '-', '*', '/']
if op not in oplist:
    print("НЕКОРРЕКТНАЯ ОПЕРАЦИЯ")
elif (op == '+'):
    print(a+b)
elif (op == '-'):
    print(a-b)
elif (op == '*'):
    print(a*b)
elif (op == '/'):
    try:
        print(a/b)
    except ZeroDivisionError:
        print("ДЕЛИТЬ НА 0 НЕЛЬЗЯ!")