import subprocess
import sys


class AppUpdater:
    @staticmethod
    def check_and_update():
        print("Проверка обновлений...")

        try:
            subprocess.run(["git", "--version"],
                           check=True,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)

            subprocess.run(["git", "fetch"],
                           check=True,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            result = subprocess.run(
                ["git", "rev-list", "HEAD..origin/main", "--count"],
                capture_output=True,
                text=True,
                check=True
            )

            new_commits = int(result.stdout.strip())

            if new_commits == 0:
                print("У вас последняя версия.\n")
                return

            print(f"\nНайдено обновление ({new_commits} изменений)")
            answer = input("Обновить сейчас? (да/нет): ").strip().lower()

            if answer not in ["да", "yes"]:
                print("Обновление отложено.\n")
                return

            print("\nЗагрузка обновлений...")
            subprocess.run(["git", "pull"], check=True)

            print("\nПроект обновлен! Перезапустите программу.")
            sys.exit(0)

        except FileNotFoundError:
            print("Git не установлен (обновление невозможно)")
        except subprocess.CalledProcessError:
            print("Не удалось проверить обновления (нет сети?)")
        except Exception as e:
            print(f"Ошибка при проверке обновлений: {e}")

