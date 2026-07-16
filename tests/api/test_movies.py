import pytest
import requests
from utils.data_generator import DataGenerator

class TestMoviesApi:

    @pytest.mark.parametrize("location", ["MSK", "SPB"])
    def test_get_movies_filter_by_location(self, common_user, location):
        response = common_user.api.movies_api.get_movies(params={"locations": location})
        movies= response.json()["movies"]
        assert len(movies) > 0
        for movie in movies:
            assert movie["location"] == location



    def test_edit_movie(self, super_admin, created_movie):
        movie_id = created_movie["id"]
        payload = {"name": "Updated Movie Name"}
        response = super_admin.api.movies_api.edit_movie(movie_id, payload)
        assert response.json()["name"] == "Updated Movie Name"


    def test_create_movie_unauthorized(self, unauthenticated_api_manager):
        payload = DataGenerator.generate_random_movie_data()
        unauthenticated_api_manager.movies_api.create_movie(payload, expected_status=401)


    def test_create_movie_forbidden_for_common_user(self, common_user):
        payload = DataGenerator.generate_random_movie_data()
        common_user.api.movies_api.create_movie(payload, expected_status=403)

    @pytest.mark.parametrize("user_fixture, expected_status", [
        ("super_admin", 200),
        ("admin_user", 403),
        ("common_user", 403)
    ], ids=["Superadmin can delete", "Admin cannot delete", "User cannot delete"])
    def test_delete_movie_permissions(self, request, user_fixture, expected_status, super_admin):
        movie_payload = DataGenerator.generate_random_movie_data()
        movie = super_admin.api.movies_api.create_movie(movie_payload).json()
        movie_id = movie["id"]

        user = request.getfixturevalue(user_fixture)

        user.api.movies_api.delete_movie(movie_id, expected_status=expected_status)

        if expected_status == 403:
            super_admin.api.movies_api.delete_movie(movie_id, expected_status=200)