import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "doctorai")

client = MongoClient("mongodb+srv://vishrutrela:Vishrut123@cluster0.idwtat0.mongodb.net/doctorai")
db = client["doctorai"]

print(client)

def get_database():
    return db
