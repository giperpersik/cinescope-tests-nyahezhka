import allure
import pytest
from playwright.sync_api import sync_playwright
from pages.page_object_models import CinescopLoginPage, CinescopRegisterPage, CinescopMoviePage
from utils.data_generator import DataGenerator


@allure.epic("Тестирование UI")
@allure.feature("Тестирование Страницы Фильма")
@pytest.mark.ui
class TestMovieReviewPage:
    @allure.title("Оставление отзыва под фильмом")
    def test_leave_movie_review_by_ui(self):
        with sync_playwright() as playwright:
            random_email = DataGenerator.generate_random_email()
            random_name = DataGenerator.generate_random_name()
            random_password = DataGenerator.generate_random_password()
            review_text = f"Отличный фильм! {DataGenerator.generate_random_int(6)}"

            browser = playwright.chromium.launch(headless=False)
            page = browser.new_page()

            # 1. Регистрация нового пользователя через UI
            register_page = CinescopRegisterPage(page)
            register_page.open()
            register_page.register(
                f"PlaywrightTest {random_name}",
                random_email,
                random_password,
                random_password
            )
            register_page.assert_was_redirect_to_login_page()

            # 2. Логин в систему через UI
            login_page = CinescopLoginPage(page)
            login_page.login(random_email, random_password)
            page.wait_for_timeout(2000)

            # 3. Переход на страницу фильма и добавление отзыва
            movie_page = CinescopMoviePage(page)
            movie_page.open_movie_page("65865")
            movie_page.add_review(review_text, rating="5")
            movie_page.make_screenshot_and_attach_to_allure()
            movie_page.assert_review_was_added(review_text)

            browser.close()
