import hashlib
from db_manager import DBManager


class TestDatabaseConnection:

    def test_connection_success(self):
        db = DBManager()
        conn = db.get_connection()

        assert conn is not None
        conn.close()

    def test_check_user_returns_tuple(self):
        db = DBManager()
        password_hash = hashlib.sha256("admin123".encode()).hexdigest()
        user = db.check_user("admin", password_hash)

        if user:
            assert isinstance(user, tuple)
            assert len(user) == 3
            assert isinstance(user[0], int)
            assert isinstance(user[1], str)
            assert isinstance(user[2], str)

    def test_add_and_load_note(self):
        db = DBManager()
        db.add_note(1, "TEST_SERVER", "Тестовая заметка для проверки БД")
        notes = db.load_notes(1)

        assert len(notes) > 0
        texts = [note[1] for note in notes]
        assert "Тестовая заметка для проверки БД" in texts

    def test_add_metrics(self):
        db = DBManager()
        db.add_metrics("TEST_SERVER", 45.5, 62.3, 78.1)
        metrics = db.load_metrics()

        assert len(metrics) > 0
        last_metric = metrics[0]
        assert len(last_metric) == 5

    def test_add_security_log(self):
        db = DBManager()
        db.add_security_log("TEST_SERVER", "Тестовая запись лога")
        logs = db.load_security_logs()

        assert len(logs) > 0
        messages = [log[1] for log in logs]
        assert "Тестовая запись лога" in messages


class TestNotes:

    def setup_method(self):
        self.db = DBManager()

    def test_add_note(self):
        self.db.add_note(1, "TEST_SERVER", "Тест добавления заметки")
        notes = self.db.load_notes(1)

        texts = [n[1] for n in notes]
        assert "Тест добавления заметки" in texts

    def test_delete_note(self):
        self.db.add_note(1, "TEST_SERVER", "Заметка для удаления")

        notes_before = self.db.load_notes(1)
        count_before = len(notes_before)
        print(f"\nЗаметок до удаления: {count_before}")

        all_notes = self.db.load_all_notes()
        note_id = None
        for note in all_notes:
            if note[3] == "Заметка для удаления":
                note_id = note[0]
                break

        print(f"Найден note_id: {note_id}, тип: {type(note_id)}")

        if note_id:
            result = self.db.delete_note(note_id, 1)
            print(f"Результат удаления: {result}")
            assert result is True

            notes_after = self.db.load_notes(1)
            count_after = len(notes_after)
            print(f"Заметок после удаления: {count_after}")

            assert count_after == count_before - 1, \
                f"Ожидалось {count_before - 1} заметок, получилось {count_after}"

    def test_load_all_notes_for_admin(self):

        notes = self.db.load_all_notes()
        assert isinstance(notes, list)