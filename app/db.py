from pymongo import MongoClient
from app.config import MONGODB_URI, MONGO_DB_NAME

client = MongoClient("mongodb+srv://vishrutrela:Vishrut123@cluster0.idwtat0.mongodb.net/doctorai")
db = client[doctorai]
