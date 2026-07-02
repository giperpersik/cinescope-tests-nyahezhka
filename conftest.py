import requests
from constants import AUTH_URL, HEADERS, REGISTER_ENDPOINT, LOGIN_ENDPOINT
import pytest
from custom_requester.custom_requester import CustomRequester
from config.base_urls import AUTH_BASE_URL
from utils.data_generator import DataGenerator
from clients.api_manager import ApiManager

@pytest.fixture(scope="function")
def test_user():
    password = DataGenerator.generate_random_password()
    return{
            "email": DataGenerator.generate_random_email(),
            "fullName": DataGenerator.generate_random_name(),
            "password": password,
            "passwordRepeat":password
    }

@pytest.fixture(scope="session")
def base_session():
    return requests.Session()


@pytest.fixture(scope="session")
def api_manager(base_session):
    return ApiManager(base_session)


@pytest.fixture(scope="session")
def unauthenticated_api_manager():
    session = requests.Session()
    yield ApiManager(session)
    session.close()

@pytest.fixture(scope="function")
def registered_user(api_manager, test_user):
    response = api_manager.auth_api.register_user(test_user).json()
    test_user["id"] = response["id"]
    return test_user


@pytest.fixture(scope="session")
def admin_api_manager():
    session = requests.Session()
    manager = ApiManager(session)
    manager.auth_api.authenticate(("api1@gmail.com", "asdqwe123Q"))
    yield manager
    session.close()


@pytest.fixture(scope="function")
def created_movie(admin_api_manager):
    movie_payload = DataGenerator.generate_random_movie_data()
    response = admin_api_manager.movies_api.create_movie(movie_payload).json()
    yield response
    admin_api_manager.movies_api.delete_movie(response["id"], expected_status=[200, 404])

