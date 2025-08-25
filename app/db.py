from pymongo import MongoClient
from app.config import MONGODB_URI, MONGO_DB_NAME

client = MongoClient(MONGODB_URI)
db = client[MONGO_DB_NAME]
