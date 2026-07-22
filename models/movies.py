from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class MovieItem(BaseModel):
    """
    Pydantic модель одного фильма (Movie).
    Используется для валидации структуры и типов данных ответа от сервера.
    """
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: Optional[int] = Field(default=None, description="Уникальный идентификатор фильма (ID)")
    name: str = Field(..., description="Название фильма")
    price: int = Field(..., description="Стоимость билета/фильма")
    description: Optional[str] = Field(default=None, description="Описание фильма")
    image_url: Optional[str] = Field(default=None, alias="imageUrl", description="URL обложки фильма")
    location: Optional[str] = Field(default=None, description="Город/Локация (MSK, SPB и т.д.)")
    published: Optional[bool] = Field(default=True, description="Опубликован ли фильм")
    rating: Optional[float] = Field(default=0.0, description="Рейтинг фильма")
    genre_id: Optional[int] = Field(default=None, alias="genreId", description="ID жанра фильма")
    created_at: Optional[str] = Field(default=None, alias="createdAt", description="Дата и время создания фильма в ISO формате")


class MoviesListResponse(BaseModel):
    """
    Pydantic модель ответа сервера при запросе списка фильмов GET /movies.
    Валидирует верхнеуровневый массив 'movies'.
    """
    model_config = ConfigDict(extra="ignore")

    movies: List[MovieItem] = Field(..., description="Список фильмов, возвращаемых сервером")
