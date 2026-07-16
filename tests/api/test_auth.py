from constants import REGISTER_ENDPOINT, LOGIN_ENDPOINT
from models.user import RegisterUserResponse
import pytest
import requests
from utils.data_generator import DataGenerator


class TestAuthApi:
    def test_register_user(self, api_manager, test_user):
        response = api_manager.auth_api.register_user(test_user)

        register_user_response = RegisterUserResponse(**response.json())
        assert register_user_response.email == test_user.email

    def test_login_user(self, api_manager, test_user, registered_user):

        login_data = {
            "email": registered_user.email,
            "password": registered_user.password
        }

        response = api_manager.auth_api.login_user(login_data)

        response_json = response.json()
        access_token = response_json.get("accessToken")

        user_info = response_json.get("user", {})
        email = user_info.get("email")
        assert access_token is not None, "Токен отсуствует в ответе 🍆"
        assert email == registered_user.email


    def test_login_user_incorrect_password(self, api_manager, registered_user):
        login_data_incorrect = {
            "email": registered_user.email,
            "password": "wrong_password_for_test"
        }

        response = api_manager.auth_api.login_user(login_data_incorrect, expected_status=401)

        assert response.json().get("message") == "Неверный логин или пароль", "Некорректное сообщение об ошибке"


    def test_login_user_non_existent_email(self, api_manager):

        non_existent_email = DataGenerator.generate_random_email()

        login_non_existent_email = {
            "email": non_existent_email,
            "password": "password_huizalupa"
        }

        response = api_manager.auth_api.login_user(login_non_existent_email, expected_status=401)
        assert response.json().get("message") == "Неверный логин или пароль", "Некорректное сообщение об ошибке"


    def test_login_user_empty_body(self, api_manager):
        response = api_manager.auth_api.login_user({}, expected_status = 401)

        assert response.json().get("message") == "Неверный логин или пароль", "Некорректное сообщение об ошибке"



    def test_get_user_info_unauthorized(self, unauthenticated_api_manager,  registered_user):
        user_id = registered_user.id
        response = unauthenticated_api_manager.user_api.get_user_info(user_id, expected_status=401)

    def test_register_timeout(self, api_manager, test_user):
        with pytest.raises(requests.exceptions.Timeout):
            api_manager.auth_api.register_user(test_user, timeout=0.001)

    def test_delete_multiple_users(self, api_manager):
        user_ids = []
        last_creds = None
        for _ in range(3):
            email = DataGenerator.generate_random_email()
            name = DataGenerator.generate_random_name()
            password = DataGenerator.generate_random_password()
            user_data = {
                "email": email,
                "fullName": name,
                "password": password,
                "passwordRepeat": password
            }
            resp = api_manager.auth_api.register_user(user_data).json()
            user_ids.append(resp["id"])
            last_creds = (email, password)
        
        # Authenticate to get access token in session
        api_manager.auth_api.authenticate(last_creds)
        
        # Delete multiple users using *args forwarding and allowing 200 or 403 status codes
        api_manager.user_api.delete_users(*user_ids, expected_status=[200, 403])


