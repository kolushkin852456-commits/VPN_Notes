import os
import hashlib
from db_manager import DBManager
from config import Configuration


class TestAuthorization:

    def setup_method(self):
        self.db = DBManager()

    def test_successful_login(self):
        password_hash = hashlib.sha256("admin123".encode()).hexdigest()
        user = self.db.check_user("admin", password_hash)

        assert user is not None
        assert user[1] == "admin"
        assert user[2] == "admin"

    def test_nonexistent_user(self):
        password_hash = hashlib.sha256("gv445gb58df".encode()).hexdigest()
        user = self.db.check_user("Hahah_accaunt", password_hash)

        assert user is None

    def test_session_file_creation(self):
        if os.path.exists(Configuration.SESSION_FILE):
            os.remove(Configuration.SESSION_FILE)

        password_hash = hashlib.sha256("admin123".encode()).hexdigest()
        user = self.db.check_user("admin", password_hash)

        if user:
            user_id, name, role = user
            with open(Configuration.SESSION_FILE, "w", encoding="utf-8") as f:
                f.write(f"{user_id},{name},{role}")

        assert os.path.exists(Configuration.SESSION_FILE)

        with open(Configuration.SESSION_FILE, "r", encoding="utf-8") as f:
            data = f.read().split(",")
            assert len(data) == 3
            assert data[1] == "admin"

        os.remove(Configuration.SESSION_FILE)