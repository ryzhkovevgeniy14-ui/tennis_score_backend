from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import DATABASE_URL


# Асинхронный движок SQLAlchemy
async_engine = create_async_engine(DATABASE_URL, echo=True)

# Фабрика асинхронных сессий
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)