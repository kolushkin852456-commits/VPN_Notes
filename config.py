import socket

class Configuration:

    NPGSQL_CONNECTION = {
            "host": "localhost",
            "database": "VPN_Notes",
            "user": "postgres",
            "password": "5555555555",
            "port": "5432"
    }

    VERSION = "1.0.0"
    SERVER_NAME = socket.gethostname()
    SESSION_FILE = ".session_token"