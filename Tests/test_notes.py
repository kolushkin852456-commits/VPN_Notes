from db_manager import DBManager

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