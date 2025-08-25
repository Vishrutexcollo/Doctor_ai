from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URI = os.getenv("mongodb+srv://vishrutrela:Vishrut123@cluster0.idwtat0.mongodb.net/doctorai")
MONGO_DB_NAME = os.getenv("doctorai")
OPENAI_API_KEY = os.getenv("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")
