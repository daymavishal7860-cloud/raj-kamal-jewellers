from pymongo import MongoClient
from pymongo.errors import PyMongoError
from flask import current_app
from urllib.parse import urlparse
import time


class Mongo:
    def __init__(self):
        self.client = None
        self.db = None
        self._last_check_at = 0
        self._last_check_result = False

    def init_app(self, app):
        self.client = MongoClient(
            app.config["MONGO_URI"],
            serverSelectionTimeoutMS=800,
            connectTimeoutMS=800,
            socketTimeoutMS=1200,
        )
        db_name = urlparse(app.config["MONGO_URI"]).path.strip("/") or "rajkamal_jewellers"
        self.db = self.client[db_name]
        app.config["UPLOAD_FOLDER"].mkdir(parents=True, exist_ok=True)

    def is_connected(self):
        now = time.monotonic()
        if now - self._last_check_at < 30:
            return self._last_check_result

        try:
            self.client.admin.command("ping")
            self._last_check_at = now
            self._last_check_result = True
            return True
        except PyMongoError as exc:
            self._last_check_at = now
            self._last_check_result = False
            current_app.logger.warning("MongoDB is not reachable; using empty query results.")
            current_app.logger.debug("MongoDB connection error: %s", exc)
            return False


mongo = Mongo()
