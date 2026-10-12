def f(a:float, b:float, op:str):
    oplist = ['+', '-', '*', '/']
    flist = [lambda a,b: a+b, lambda a,b: a-b, lambda a,b: a*b, lambda a,b: a/b]
    try:
        print(flist[oplist.index(op)](a, b))
    except ValueError:
        print("НЕКОРРЕКТНАЯ ОПЕРАЦИЯ!")
    except ZeroDivisionError:
        print("ДЕЛИТЬ НА 0 НЕЛЬЗЯ!")

while True:
    a = float(input("ВВЕДИТЕ ОПЕРАНД 1:   "))
    op = input('ВВЕДИТЕ ОПЕРАЦИЮ [ОДИН ИЗ: +,-,*,/]:   ')
    b = float(input("ВВЕДИТЕ ОПЕРАНД 2:   "))

    print("РЕЗУЛЬТАТ ОПЕРАЦИ:   ")
    f(a,b,op)