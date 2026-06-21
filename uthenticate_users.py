import hashlib
import os
from config import Configuration
from exceptions import VpnAppError


class Authenticate:

    @staticmethod
    def authenticate(db_instance):
        if os.path.exists(Configuration.SESSION_FILE):
            with open(Configuration.SESSION_FILE, "r", encoding="utf-8") as f:
                data = f.read().split(",")
                if len(data) == 3:
                    return int(data[0]), data[1], data[2]

        print("--- Вход в систему управления Notes ---")
        username = input("Введите логин: ")
        password = input("Введите пароль: ")

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        user = db_instance.check_user(username, password_hash)

        if user:
            user_id, name, role = user
            with open(Configuration.SESSION_FILE, "w", encoding="utf-8") as f:
                f.write(f"{user_id},{name},{role}")
            print(f" Успешный вход! Ваша роль: {role}\n")
            return user_id, name, role
        else:
            db_instance.add_security_log(Configuration.SERVER_NAME, f"Неудачная попытка входа под именем: {username}")
            raise VpnAppError("AUTH")