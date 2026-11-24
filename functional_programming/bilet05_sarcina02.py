# Al doilea maxim: find second biggest numer in a list

lis = [983342, 123, 54538, 32423]


def second_max(lis):
    return sorted(lis)[-2] if lis else []


print(second_max(lis))
