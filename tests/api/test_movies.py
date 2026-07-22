import allure
import pytest
import requests
from models.movies import MoviesListResponse, MovieItem
from utils.data_generator import DataGenerator


@allure.epic("Movies API")
@allure.feature("Тестирование сервиса фильмов /movies")
@pytest.mark.api
@pytest.mark.movies
class TestMoviesApi:

    @allure.story("Фильтрация фильмов по локации")
    @allure.title("Получение списка фильмов с фильтрацией по локации {location}")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("location", ["MSK", "SPB"])
    def test_get_movies_filter_by_location(self, common_user, location):
        with allure.step(f"Отправка GET запроса /movies с параметром location={location}"):
            response = common_user.api.movies_api.get_movies(params={"locations": location})

        with allure.step("Валидация ответа сервера через Pydantic схему MoviesListResponse"):
            validated_data = MoviesListResponse.model_validate(response.json())

        with allure.step(f"Проверка, что фильмы получены и каждый фильм имеет локацию {location}"):
            movies = validated_data.movies
            assert len(movies) > 0, "Список фильмов не должен быть пустым"
            for movie in movies:
                assert movie.location == location, f"Локация фильма {movie.name} ({movie.location}) не совпадает с запрашиваемой {location}"

    @allure.story("Редактирование фильмов")
    @allure.title("Успешное редактирование фильма супер-администратором")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_edit_movie(self, super_admin, created_movie):
        movie_id = created_movie["id"]
        payload = {"name": "Updated Movie Name"}

        with allure.step(f"Отправка PATCH запроса /movies/{movie_id} для обновления названия"):
            response = super_admin.api.movies_api.edit_movie(movie_id, payload)

        with allure.step("Валидация обновленного фильма через Pydantic модель MovieItem"):
            movie = MovieItem.model_validate(response.json())

        with allure.step("Проверка обновленного названия фильма"):
            assert movie.name == "Updated Movie Name"

    @allure.story("Права доступа при создании фильмов")
    @allure.title("Запрет создания фильма неавторизованным пользователем (401)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_movie_unauthorized(self, unauthenticated_api_manager):
        with allure.step("Генерация тестовых данных фильма"):
            payload = DataGenerator.generate_random_movie_data()

        with allure.step("Отправка POST запроса /movies без авторизации (ожидается статус 401)"):
            unauthenticated_api_manager.movies_api.create_movie(payload, expected_status=401)

    @allure.story("Права доступа при создании фильмов")
    @allure.title("Запрет создания фильма обычным пользователем (403)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_movie_forbidden_for_common_user(self, common_user):
        with allure.step("Генерация тестовых данных фильма"):
            payload = DataGenerator.generate_random_movie_data()

        with allure.step("Отправка POST запроса /movies обычным пользователем (ожидается статус 403)"):
            common_user.api.movies_api.create_movie(payload, expected_status=403)

    @allure.story("Права доступа при удалении фильмов")
    @allure.title("Проверка прав на удаление фильма для ролей: {user_fixture}")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("user_fixture, expected_status", [
        ("super_admin", 200),
        ("admin_user", 403),
        ("common_user", 403)
    ], ids=["Superadmin can delete", "Admin cannot delete", "User cannot delete"])
    def test_delete_movie_permissions(self, request, user_fixture, expected_status, super_admin):
        with allure.step("Создание тестового фильма супер-администратором"):
            movie_payload = DataGenerator.generate_random_movie_data()
            create_response = super_admin.api.movies_api.create_movie(movie_payload)
            movie_data = MovieItem.model_validate(create_response.json())
            movie_id = movie_data.id

        with allure.step(f"Получение фикстуры пользователя '{user_fixture}'"):
            user = request.getfixturevalue(user_fixture)

        with allure.step(f"Попытка удаления фильма ID={movie_id} ролью {user_fixture} (ожидается статус {expected_status})"):
            user.api.movies_api.delete_movie(movie_id, expected_status=expected_status)

        if expected_status == 403:
            with allure.step("Очистка: удаление созданного фильма супер-администратором"):
                super_admin.api.movies_api.delete_movie(movie_id, expected_status=200)

    @allure.story("Интеграция с Базой Данных (БД)")
    @allure.title("Проверка создания и удаления фильма в БД PostgreSQL")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.regression
    def test_create_and_delete_movie_db_verification(self, super_admin, db):
        with allure.step("Подготовка уникального названия фильма и проверка его отсутствия в БД"):
            movie_payload = DataGenerator.generate_random_movie_data()
            movie_name = movie_payload["name"]
            movie_in_db = db.get_movie_by_name(movie_name)
            assert movie_in_db is None, "Фильм не должен существовать в базе данных до создания!"

        with allure.step("Создание фильма через API"):
            create_response = super_admin.api.movies_api.create_movie(movie_payload)
            movie = MovieItem.model_validate(create_response.json())
            movie_id = movie.id

        with allure.step("Проверка появления фильма в базе данных по имени и по ID"):
            check_created_movie = db.get_movie_by_name(movie_name)
            assert check_created_movie is not None, "Фильм не найден в базе данных после создания!"
            assert check_created_movie.id == movie_id, "ID фильма в базе не совпадает с ID в ответе API!"

        with allure.step("Удаление фильма через API"):
            super_admin.api.movies_api.delete_movie(movie_id)

        with allure.step("Проверка физического удаления фильма из базы данных"):
            movie_last_check = db.get_movie_by_name(movie_name)
            assert movie_last_check is None, "Фильм все еще существует в базе данных после удаления!"