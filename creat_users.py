import hashlib
import psycopg2
from config import Configuration


def create_test_users():
    test_users = [
        ("admin", "admin123", "admin"),
        ("operator", "user123", "user"),
        ("bot", "bot123", "user")
    ]

    try:
        print(" Подключение к базе данных PostgreSQL...")

        with psycopg2.connect(**Configuration.NPGSQL_CONNECTION) as conn:
            with conn.cursor() as cursor:
                print(" Очистка старых записей из таблицы пользователей...")
                cursor.execute("TRUNCATE TABLE users RESTART IDENTITY CASCADE;")

                print(" Генерация хэшей и внесение пользователей в БД...")
                for username, password, role in test_users:
                    password_hash = hashlib.sha256(password.encode()).hexdigest()

                    cursor.execute(
                        "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s);",
                        (username, password_hash, role)
                    )
                    print(f" Добавлен: {username} | Пароль: {password} | Роль: {role}")


        print("\nВсе 3 тестовых пользователя успешно добавлены в базу данных!")
        print(" Соединение с СУБД закрыто.")

    except Exception as e:
        print(f"\nНе удалось внести пользователей: {e}")
        print("Проверьте, запущена ли PostgreSQL и создана ли таблица 'users'.")


if __name__ == "__main__":
    create_test_users()

