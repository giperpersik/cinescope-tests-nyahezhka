from models.user import TestUser
import requests
from constants import AUTH_URL, HEADERS, REGISTER_ENDPOINT, LOGIN_ENDPOINT
import pytest
from custom_requester.custom_requester import CustomRequester
from config.base_urls import AUTH_BASE_URL
from utils.data_generator import DataGenerator
from clients.api_manager import ApiManager
from entities.user import User
from resources.user_creds import SuperAdminCreds
from constants.roles import Roles
from sqlalchemy.orm import Session
from database.db_client import get_db_session
from database.db_helpers import DBHelper


@pytest.fixture(scope="function")
def test_user() -> TestUser:
    password = DataGenerator.generate_random_password()
    return TestUser(
        email=DataGenerator.generate_random_email(),
        fullName=DataGenerator.generate_random_name(),
        password=password,
        passwordRepeat=password,
        roles=[Roles.USER]  # Передаем сам Enum Roles.USER
    )

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
def registered_user(api_manager, test_user: TestUser) -> TestUser:
    response = api_manager.auth_api.register_user(test_user).json()
    test_user.id = response["id"]  # Теперь пишем через точку!
    return test_user


@pytest.fixture(scope="session")
def admin_api_manager():
    session = requests.Session()
    manager = ApiManager(session)
    manager.auth_api.authenticate(("api1@gmail.com", "asdqwe123Q"))
    yield manager
    session.close()


@pytest.fixture(scope="function")
def created_movie(super_admin):
    movie_payload = DataGenerator.generate_random_movie_data()
    response = super_admin.api.movies_api.create_movie(movie_payload).json()
    yield response
    super_admin.api.movies_api.delete_movie(response["id"], expected_status=[200, 404])


@pytest.fixture
def super_admin():
    session = requests.Session()
    new_session = ApiManager(session)

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session
    )

    super_admin.api.auth_api.authenticate(super_admin.creds)
    yield super_admin
    session.close()


@pytest.fixture
def super_admin_token():
    session = requests.Session()
    api = ApiManager(session)
    response = api.auth_api.login_user({
        "email": SuperAdminCreds.USERNAME,
        "password": SuperAdminCreds.PASSWORD
        }).json()
    token = response["accessToken"]
    yield token
    session.close()




@pytest.fixture
def creation_user_data(test_user: TestUser) -> TestUser:
    return test_user.model_copy(update={
        "verified": True,
        "banned": False
    })


@pytest.fixture
def common_user(super_admin, creation_user_data: TestUser):
    session = requests.Session()
    new_session = ApiManager(session)

    common_user = User(
        creation_user_data.email,
        creation_user_data.password,
        [Roles.USER.value],
        new_session
    )

    super_admin.api.user_api.create_user(creation_user_data)
    common_user.api.auth_api.authenticate(common_user.creds)
    yield common_user
    session.close()


@pytest.fixture
def admin_user(super_admin, creation_user_data: TestUser):
    session = requests.Session()
    new_session = ApiManager(session)

    # Делаем копию и меняем роль на ADMIN
    admin_user_data = creation_user_data.model_copy(update={
        "roles": [Roles.ADMIN]
    })

    admin_user = User(
        admin_user_data.email,
        admin_user_data.password,
        [Roles.ADMIN.value],
        new_session
    )

    super_admin.api.user_api.create_user(admin_user_data)
    admin_user.api.auth_api.authenticate(admin_user.creds)
    yield admin_user
    session.close()


@pytest.fixture(scope="module")
def db_session():
    session = get_db_session()
    yield session
    session.close()


@pytest.fixture(scope="module")
def db(db_session) -> DBHelper:
    return DBHelper(db_session)



