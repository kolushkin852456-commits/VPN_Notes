class ConsoleCommand:

    @staticmethod
    def print_markdown_help(role):
        print("СПРАВКА ПО КОМАНДАМ СИСТЕМЫ VPN NOTES")
        print("=" * 60)

        print("\n## Общие команды (для всех ролей):")
        print("* `help`       - Показать эту справку")
        print("* `logout`     - Выйти из текущей сессии")
        print("* `exit`       - Завершить работу программы")

        if role in ["admin", "user"]:
            print("\nКоманды для заметок (admin, user):")
            print("* `addNewNote \"текст\"` - Создать новую заметку")
            print("* `viewNotes`            - Посмотреть свои заметки")
            print("* `deleteNote`           - Удалить заметку по ID")

        if role == "admin":
            print("\nКоманды администратора (только admin):")
            print("* `viewMetrics`    - Посмотреть историю нагрузки")
            print("* `start_watchdog` - Запустить мониторинг в фоне")
            print("* `stop_watchdog`  - Остановить мониторинг")
            print("* `viewLogs`       - Посмотреть логи безопасности")
            print("* `viewUsers`      - Посмотреть список всех пользователей")
            print("* `deleteUser`     - Удалить пользователя по ID")
