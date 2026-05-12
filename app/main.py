from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from app.routers import players, matches


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Выполняется при запуске и остановке сервера"""

    print("Выполнение миграций...")
    from app.migrate import run_migrations
    await asyncio.to_thread(run_migrations)
    print("Миграции выполнены")

    yield


app = FastAPI(lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(players.router)
app.include_router(matches.router)


@app.get("/")
async def root():
    return {'message': 'Welcome to the Tennis Score API!'}