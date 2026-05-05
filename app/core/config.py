import os
from dotenv import load_dotenv


# Загружаем переменные окружения из файла .env
load_dotenv()

# URL подключения к БД. В Docker используется db:5432, локально localhost:5432
DATABASE_URL: str = os.getenv("DATABASE_URL")