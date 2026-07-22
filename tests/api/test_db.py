import uuid
from datetime import datetime
from db_models.user import UserDBModel


def test_create_and_find_user_in_db(db):
    # 1. Готовим уникальные данные
    user_id = str(uuid.uuid4())
    email = f"test_db_{user_id[:8]}@example.com"

    user_payload = {
        "id": user_id,
        "email": email,
        "full_name": "Тестовый БД Юзер",
        "password": "secure_password_123",
        "verified": True,
        "banned": False,
        "roles": "{USER}",
        "created_at": datetime.now(),  # Добавили текущее время
        "updated_at": datetime.now()  # Добавили текущее время
    }

    # 2. Создаем пользователя через хелпер
    created_user = db.create_test_user(user_payload)

    # 3. Ищем этого пользователя в базе
    found_user = db.get_user_by_email(email)

    # 4. Проверяем, что всё записалось верно
    assert found_user is not None
    assert found_user.id == user_id
    assert found_user.full_name == "Тестовый БД Юзер"

    # 5. Удаляем мусор
    db.delete_user(found_user)