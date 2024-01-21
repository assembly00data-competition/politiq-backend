from pymongo import MongoClient
from dotenv import load_dotenv
import os

class MongoDBConnection:
    def __init__(self):
        load_dotenv()  # 환경변수 로드
        self.uri = os.getenv("MONGO_URI")
        self.db_name = os.getenv("MONGO_DB_NAME")
        self.client = None
        self.db = None

    def connect(self):
        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def close(self):
        if self.client:
            self.client.close()
