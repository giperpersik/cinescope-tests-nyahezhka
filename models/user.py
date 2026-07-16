import datetime
from pydantic import BaseModel, field_validator, Field
from constants.roles import Roles
from typing import Optional


class UserRegistration(BaseModel):
    email: str
    fullName: str
    password: str
    passwordRepeat: str
    roles: list[Roles]
    banned: Optional[bool] = None
    verified: Optional[bool] = None

    @field_validator("email")
    def check_email(cls, value: str) -> str:
        if "@" not in value:
            raise ValueError("Email должен содержать символ @")

        return value


    @field_validator("password")
    def check_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Минимальная длинна пароля 8 символов")

        return value



class TestUser(BaseModel):
    id: Optional[str] = None
    email: str
    fullName: str
    password: str
    passwordRepeat: str = Field(..., min_length=1, max_length=20, description="Пароли должны совпадать")
    roles: list[Roles] = [Roles.USER]
    verified: Optional[bool] = None
    banned: Optional[bool] = None

    @field_validator("passwordRepeat")
    def check_password_repeat(cls, value: str, info) -> str:
        if "password" in info.data and value != info.data["password"]:
            raise ValueError("Пароли не совпадают")
        return value

    class Config:
        json_encoders = {
            Roles: lambda v: v.value
        }



class RegisterUserResponse(BaseModel):
    id: str
    email: str = Field(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    fullName: str = Field(min_length=1, max_length=100)
    verified: bool
    banned: bool
    roles: list[Roles]
    createdAt: str

    @field_validator("createdAt")
    def validate_created_at(cls, value: str) -> str:
        try:
            datetime.datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("Некорректный формат даты и времени. Ожидается формат ISO 8601.")
        return value