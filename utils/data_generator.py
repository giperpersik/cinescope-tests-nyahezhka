import random
import string
from faker import Faker
faker = Faker()

class DataGenerator:
    @staticmethod
    def generate_random_email():
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"kek{random_string}@gmail.com"

    @staticmethod
    def generate_random_name():
        return f"{faker.first_name()} {faker.last_name()}"

    @staticmethod
    def generate_random_int(length=10):
        return random.randint(10**(length-1), (10**length)-1)

    @staticmethod
    def generate_random_password():
        letter = random.choice(string.ascii_letters)  # гарантированно 1 буква
        digit = random.choice(string.digits)  # гарантированно 1 цифра
        special_chars = "?@#$%^&*|:"
        all_chars = string.ascii_letters + string.digits + special_chars
        remaining_length = random.randint(6, 18)  # Остальная длина пароля
        remaining_chars = ''.join(random.choices(all_chars, k=remaining_length))

        password = list(letter + digit + remaining_chars)
        random.shuffle(password)

        return ''.join(password)

    @staticmethod
    def generate_random_movie_data():
        return {
            "name": f"Test Movie {faker.word().capitalize()} {random.randint(10000, 99999)}",
            "description": faker.text(max_nb_chars=100),
            "price": random.randint(100, 1000),
            "location": random.choice(["MSK", "SPB"]),
            "published": True,
            "genreId": random.randint(4, 10)
        }








