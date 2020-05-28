import numpy as np
count = 0                            # счетчик попыток
number = np.random.randint(1, 101)    # загадали число
print("Загадано число от 1 до 100")


def score_game(game_core):
    '''Запускаем игру 1000 раз, чтобы узнать,
    как быстро игра угадывает число'''
    count_ls = []

    # фиксируем RANDOM SEED, чтобы ваш эксперимент был воспроизводим!
    np.random.seed(1)
    random_array = np.random.randint(1, 101, size=(1000))
    for number in random_array:
        count_ls.append(game_core(number))
    score = int(np.mean(count_ls))
    print(f"Ваш алгоритм угадывает число в среднем за {score} попыток")
    return(score)


def guess_number(number):
    '''угадываем число: на каждой попытке уточняем диапазон, в котором стоит
    выбирать число Х для проверки.
    если загаданное число больше Х: тогда нет смысла искать среди чисел 1..Х
    если загаданное число меньше Х: не ищем среди чисел Х..100
    начинаем с диапазона 1..100'''
    count = 1
    min_border = 1
    max_border = 101
    predict = np.random.randint(min_border, max_border)

    while number != predict:
        if number > predict:
            min_border = predict+1
        else:
            max_border = predict
        predict = np.random.randint(min_border, max_border)
        count += 1
    return count


score_game(guess_number)
