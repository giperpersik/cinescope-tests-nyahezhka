# Практика аннотаций типов в Python

# 1. Функция multiply: принимает два целых числа и возвращает их произведение
# Напишите её ниже:
def multiply(a: int, b: int) -> int:
    return a * b


# 2. Функция sum_numbers: принимает список целых чисел и возвращает их сумму
# Напишите её ниже:
def sum_numbers(numbers: list[int]) -> int:
    return sum(numbers)



# 3. Функция find_user: принимает ID пользователя и возвращает строку (имя) или None
# Напишите её ниже:
def find_user(user_id: int) -> str | None:
    if user_id == 1:
        return "Пользователь найден"
    return None

