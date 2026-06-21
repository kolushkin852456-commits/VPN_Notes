import sys
import os
import time
import shlex
import threading
from config import Configuration
from db_manager import DBManager
from system_monitor import SystemMonitor
from updater import AppUpdater
from exceptions import VpnAppError
from console_command import ConsoleCommand
from uthenticate_users import Authenticate

watchdog_running = False
watchdog_thread = None


def watchdog_worker(db, server_name):
    global watchdog_running
    while watchdog_running:
        try:
            cpu, ram, hdd = SystemMonitor.collect_data()
            db.add_metrics(server_name, cpu, ram, hdd)
            time.sleep(5)
        except Exception as e:
            print(f"\nОшибка мониторинга: {e}")
            break


def main():
    global watchdog_running, watchdog_thread

    db = DBManager()
    AppUpdater.check_and_update()

    try:
        user_id, username, role = Authenticate.authenticate(db)
    except VpnAppError as e:
        e.print_error()
        sys.exit(1)

    ConsoleCommand.print_markdown_help(role)

    while True:
        try:
            user_input = input(f"\n[{username}@{Configuration.SERVER_NAME}]> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nЗавершение работы...")
            break

        if not user_input:
            continue

        try:
            parsed_args = shlex.split(user_input)
        except ValueError as e:
            print(f"Ошибка синтаксиса команды: {e}")
            continue

        command = parsed_args[0]

        if command == "exit":
            if watchdog_running and watchdog_thread is not None:
                watchdog_running = False
                watchdog_thread.join()
            print("Завершение работы программы. До свидания!")
            break

        if command == "logout":
            if watchdog_running and watchdog_thread is not None:
                watchdog_running = False
                watchdog_thread.join()
            if os.path.exists(Configuration.SESSION_FILE):
                os.remove(Configuration.SESSION_FILE)
                print("Сессия успешно закрыта. Перезапустите программу для новой авторизации.")
            else:
                print("Активной сессии не найдено.")
            break

        if command == "help":
            ConsoleCommand.print_markdown_help(role)
            continue

        try:
            if command == "addNewNote":
                if role not in ["admin", "user"]:
                    db.add_security_log(Configuration.SERVER_NAME, f"Попытка доступа: {username} ({role}) -> {command}")
                    raise VpnAppError("ACCESS", "Ваша роль не позволяет создавать заметки!")

                if len(parsed_args) < 2:
                    print("Ошибка: Пропущен текст заметки. Пример: addNewNote \"Текст\"")
                    continue

                note_text = parsed_args[1]
                db.add_note(user_id, Configuration.SERVER_NAME, note_text)
                print(f"Заметка успешно добавлена на сервер {Configuration.SERVER_NAME}")

            elif command == "viewNotes":
                if role not in ["admin", "user"]:
                    db.add_security_log(Configuration.SERVER_NAME, f"Попытка доступа: {username} ({role}) -> {command}")
                    raise VpnAppError("ACCESS")

                if role == "admin":
                    notes = db.load_all_notes()
                    print("\n=== ВСЕ ЗАМЕТКИ В СИСТЕМЕ ===")
                    if not notes:
                        print("В системе пока нет заметок.")
                    else:
                        for note in notes:
                            note_id, author, server, text, created = note
                            print(f"ID: {note_id}, Автор: {author}, Сервер: {server}, Текст: {text}, Дата: {created}")
                else:
                    notes = db.load_notes(user_id)
                    print("\n=== МОИ ЗАМЕТКИ ===")
                    if not notes:
                        print("У вас пока нет заметок.")
                    else:
                        for note in notes:
                            server, text, created = note
                            print(f"[{created}] Сервер: {server} -> {text}")

            elif command == "deleteNote":
                if role not in ["admin", "user"]:
                    db.add_security_log(Configuration.SERVER_NAME, f"Попытка доступа: {username} ({role}) -> {command}")
                    raise VpnAppError("ACCESS")

                if role == "admin":
                    note_id_str = input("Введите ID заметки для удаления: ").strip()
                    try:
                        note_id = int(note_id_str)
                    except ValueError:
                        print("Ошибка: ID должен быть числом.")
                        continue

                    result = db.delete_note_by_id(note_id)
                    if result:
                        print(f"Заметка ID {note_id} (автор: {result}) успешно удалена.")
                        db.add_security_log(Configuration.SERVER_NAME,f"Администратор {username} удалил заметку ID {note_id}")
                    else:
                        print(f"Заметка с ID {note_id} не найдена.")
                else:
                    note_id_str = input("Введите ID вашей заметки для удаления: ").strip()
                    try:
                        note_id = int(note_id_str)
                    except ValueError:
                        print("Ошибка: ID должен быть числом.")
                        continue

                    if db.delete_note(note_id, user_id):
                        print(f"Заметка с ID {note_id} удалена.")
                    else:
                        print("Заметка не найдена или у вас нет прав на её удаление.")

            elif command == "viewMetrics":
                rows = db.load_metrics()
                print("\n=== СТАТИСТИКА НАГРУЗКИ ИТ-ЛАНДШАФТА ===")
                if not rows:
                    print("Метрики ещё не собирались.")
                else:
                    for row in rows:
                        server, cpu, ram, hdd, created = row
                        print(f"Сервер: {server}, CPU: {cpu}%, RAM: {ram}%, HDD: {hdd}%, Время: {created}")

            elif command == "start_watchdog":
                if role != "admin":
                    db.add_security_log(Configuration.SERVER_NAME, f"Попытка доступа: {username} ({role}) -> {command}")
                    raise VpnAppError("ACCESS", "Запускать watchdog может только admin!")

                if watchdog_running:
                    print("Мониторинг уже запущен. Используйте 'stop_watchdog' для остановки.")
                    continue

                watchdog_running = True
                watchdog_thread = threading.Thread(
                    target=watchdog_worker,
                    args=(db, Configuration.SERVER_NAME),
                    daemon=True
                )
                watchdog_thread.start()
                print("Мониторинг запущен в фоновом режиме. Используйте 'stop_watchdog' для остановки.")

            elif command == "stop_watchdog":
                if not watchdog_running:
                    print("Мониторинг не запущен.")
                    continue

                watchdog_running = False
                if watchdog_thread is not None:
                    watchdog_thread.join()
                print("\nМониторинг остановлен.")
                db.add_security_log(Configuration.SERVER_NAME, f"Watchdog остановлен пользователем {username}")

            elif command == "viewLogs":
                if role != "admin":
                    db.add_security_log(Configuration.SERVER_NAME, f"Попытка доступа: {username} ({role}) -> {command}")
                    raise VpnAppError("ACCESS")

                logs = db.load_security_logs()
                print("\n=== ЛОГИ БЕЗОПАСНОСТИ СИСТЕМЫ ===")
                if not logs:
                    print("Логи безопасности пусты.")
                else:
                    for log in logs:
                        server, message, created = log
                        print(f"[{created}] Сервер: {server} -> {message}")

            elif command == "viewUsers":
                if role != "admin":
                    db.add_security_log(Configuration.SERVER_NAME, f"Попытка доступа: {username} ({role}) -> {command}")
                    raise VpnAppError("ACCESS", "Только администратор может просматривать список пользователей!")

                users = db.load_all_users()
                print("\n=== СПИСОК ВСЕХ ПОЛЬЗОВАТЕЛЕЙ СИСТЕМЫ ===")
                for u in users:
                    u_id, u_name, u_role, u_created = u
                    marker = " <- ВЫ" if u_id == user_id else ""
                    print(f"ID: {u_id}, Логин: {u_name}, Роль: {u_role}, Создан: {u_created}{marker}")

            elif command == "deleteUser":
                if role != "admin":
                    db.add_security_log(Configuration.SERVER_NAME, f"Попытка доступа: {username} ({role}) -> {command}")
                    raise VpnAppError("ACCESS", "Только администратор может удалять пользователей!")

                print("\nДоступные пользователи для удаления:")
                users = db.load_all_users()
                for u in users:
                    u_id, u_name, u_role, _ = u
                    if u_id != user_id:
                        print(f"ID: {u_id}, Логин: {u_name}, Роль: {u_role}")

                target_id_str = input("\nВведите ID пользователя для удаления: ").strip()
                try:
                    target_user_id = int(target_id_str)
                except ValueError:
                    print("Ошибка: ID должен быть числом.")
                    continue

                if target_user_id == user_id:
                    print("Ошибка: Нельзя удалить самого себя!")
                    continue

                confirm = input(
                    f"Вы уверены, что хотите удалить пользователя с ID {target_user_id}? (да/нет): ").strip().lower()
                if confirm not in ["да", "yes", "y"]:
                    print("Удаление отменено.")
                    continue

                result = db.delete_user(target_user_id)
                if result:
                    deleted_username, deleted_role = result
                    print(f"Пользователь '{deleted_username}' (роль: {deleted_role}) успешно удалён.")
                    db.add_security_log(Configuration.SERVER_NAME,f"Администратор {username} удалил пользователя {deleted_username} (ID: {target_user_id})")
                else:
                    print(f"Пользователь с ID {target_user_id} не найден.")

            else:
                print(f"Неизвестная команда: {command}. Введите 'help' для справки.")

        except VpnAppError as e:
            e.print_error()


if __name__ == "__main__":
    main()


