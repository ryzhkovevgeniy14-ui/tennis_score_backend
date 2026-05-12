import os
from dotenv import load_dotenv


# Загружаем переменные окружения из файла .env
load_dotenv()

# URL подключения к БД
DATABASE_URL: str = os.getenv("DATABASE_URL")