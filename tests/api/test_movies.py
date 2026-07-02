import pytest
import requests
from utils.data_generator import DataGenerator

class TestMoviesApi:
    def test_get_movies_filter_by_location(self, api_manager):
        response = api_manager.movies_api.get_movies(params={"locations": "MSK"})
        movies = response.json()["movies"]
        assert len(movies) > 0
        for movie in movies:
            assert movie["location"] == "MSK"



    def test_edit_movie(self, admin_api_manager, created_movie):
        movie_id = created_movie["id"]
        payload = {"name": "Updated Movie Name"}
        response = admin_api_manager.movies_api.edit_movie(movie_id, payload)
        assert response.json()["name"] == "Updated Movie Name"


    def test_create_movie_unauthorized(self, unauthenticated_api_manager):
        payload = DataGenerator.generate_random_movie_data()
        unauthenticated_api_manager.movies_api.create_movie(payload, expected_status=401)
