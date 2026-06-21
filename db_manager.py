import psycopg2
from config import Configuration

class DBManager:
    def __init__(self):
        self.config = Configuration.NPGSQL_CONNECTION

    def get_connection(self):
        return psycopg2.connect(**self.config)

    def check_user(self, username, password_hash):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, role FROM users WHERE username = %s AND password_hash = %s;",
            (username, password_hash)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user

    def add_note(self, user_id, server_name, text):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notes (user_id, server_name, note_text) VALUES (%s, %s, %s);",
            (user_id, server_name, text)
        )
        conn.commit()
        cursor.close()
        conn.close()

    def load_notes(self,user_id):

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
                             SELECT server_name, note_text, created_at FROM notes WHERE user_id = %s 
                             ORDER BY created_at DESC;
                             """,
                       (user_id,)
        )
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data

    def load_all_notes(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT notes.id, users.username, notes.server_name, notes.note_text, notes.created_at
                       FROM notes 
                       LEFT JOIN users  ON notes.user_id = users.id
                       ORDER BY notes.created_at DESC;
                       """)
        notes = cursor.fetchall()
        cursor.close()
        conn.close()

        return notes

    def add_metrics(self, server_name, cpu, ram, hdd):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO metrics (server_name, cpu_load, ram_load, hdd_load) VALUES (%s, %s, %s, %s);",
            (server_name, cpu, ram, hdd)
        )
        conn.commit()
        cursor.close()
        conn.close()

    def load_metrics(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT server_name, cpu_load, ram_load, hdd_load, created_at FROM metrics ORDER BY created_at DESC LIMIT 10;")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data

    def add_security_log(self, server_name, message):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO security_logs (server_name, log_message) VALUES (%s, %s);",
            (server_name, message)
        )
        conn.commit()
        cursor.close()
        conn.close()

    def load_security_logs(self):

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT server_name, log_message, created_at FROM security_logs ORDER BY created_at DESC LIMIT 10;")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data

    def delete_user(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s;",
                       (user_id,)
        )
        conn.commit()
        cursor.close()
        conn.close()

    def delete_note(self, note_id, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM notes WHERE id = %s AND user_id = %s;",
                (note_id, user_id)
            )
            conn.commit()
            if cursor.rowcount > 0:
                return True
            else:
                return False
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def delete_note_by_id(self, note_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT users.username FROM notes LEFT JOIN users ON notes.user_id = users.id WHERE notes.id = %s;",
                (note_id,)
            )
            result = cursor.fetchone()
            if not result:
                return None
            author_username = result[0]
            cursor.execute("DELETE FROM notes WHERE id = %s;", (note_id,))
            conn.commit()
            return author_username
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def load_all_users(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role, created_at FROM users ORDER BY id;")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return users



