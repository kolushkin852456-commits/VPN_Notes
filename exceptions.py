class VpnAppError(Exception):

    def __init__(self, error_type, message=None):
        self.error_type = error_type

        if message is None:
            if error_type == "AUTH":
                self.message = "Ошибка авторизации: Неверный логин или пароль."
            elif error_type == "ACCESS":
                self.message = "Ошибка доступа: У вашей роли нет прав на эту команду."
            else:
                self.message = "Произошла непредвиденная ошибка в системе."
        else:
            self.message = message

        super().__init__(self.message)

    def print_error(self):

        print(f"\n[{self.error_type} ERROR] {self.message}")
