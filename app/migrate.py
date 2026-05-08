from alembic.config import Config
from alembic import command
from app.core.config import DATABASE_URL


def run_migrations():
    """Выполняет миграции Alembic (синхронно)"""
    # Заменяем asyncpg на psycopg2 для миграций
    sync_url = DATABASE_URL.replace("+asyncpg", "")

    # Создаём конфиг Alembic
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", sync_url)

    # Запускаем миграции
    command.upgrade(alembic_cfg, "head")