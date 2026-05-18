from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from flask import current_app
from urllib.parse import urlparse


class Mongo:
    def __init__(self):
        self.client = None
        self.db = None

    def init_app(self, app):
        self.client = MongoClient(app.config["MONGO_URI"], serverSelectionTimeoutMS=2500)
        db_name = urlparse(app.config["MONGO_URI"]).path.strip("/") or "rajkamal_jewellers"
        self.db = self.client[db_name]
        app.config["UPLOAD_FOLDER"].mkdir(parents=True, exist_ok=True)

    def is_connected(self):
        try:
            self.client.admin.command("ping")
            return True
        except ServerSelectionTimeoutError:
            current_app.logger.warning("MongoDB is not reachable; using empty query results.")
            return False


mongo = Mongo()
