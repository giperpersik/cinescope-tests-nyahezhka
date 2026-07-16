import pytest
from pydantic import BaseModel, ValidationError
from models.user import UserRegistration

class Product(BaseModel):
    name: str
    price: float
    in_stock: bool


def test_user_registration_validation(test_user, creation_user_data):
    user = UserRegistration(**test_user.model_dump())
    assert user.email == test_user.email
    print("\nВалидированный объект пользователя:", user)
    user_simple = UserRegistration(**test_user.model_dump())
    user_full = UserRegistration(**creation_user_data.model_dump())
    json_simple = user_simple.model_dump_json(exclude_unset=True)
    json_full = user_full.model_dump_json()

    print(json_simple, json_full)


def test_user_registration_invalid_data(test_user):
    bad_email_data = test_user.model_copy(update={"email": "bad_email"})
    with pytest.raises(ValidationError):
        UserRegistration(**bad_email_data.model_dump())

def test_user_password_invalid_data(test_user):
    bad_password_data = test_user.model_copy(update={"password": "123"})
    with pytest.raises(ValidationError):
        UserRegistration(**bad_password_data.model_dump())



def test_model_json_schema():
    user_schema = UserRegistration.model_json_schema()

    print("\nJSON Schema для UserRegistration:\n", user_schema)


def test_product_serialization():
    my_product = Product(name="Keyboard", price=2500.0, in_stock=True)

    product_json = my_product.model_dump_json()
    print("\n1. Сериализованный JSON (просто текст):", product_json)

    restored_product = Product.model_validate_json(product_json)
    print("2. Десериализованный объект Python:", restored_product)