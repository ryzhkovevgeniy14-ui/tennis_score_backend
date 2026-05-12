# Tennis Score

Асинхронный REST API сервис для управления матчами, геймами, сетами,
рейтингом и статистикой игроков в большом теннисе.

## Технологии

- **FastAPI** — веб-фреймворк
- **SQLAlchemy 2.0** — ORM (асинхронный)
- **asyncpg** — драйвер PostgreSQL
- **Alembic** — миграции БД
- **Docker** — контейнеризация

## Запуск через Docker Compose

```bash
docker compose up --build
```
Если PostgreSQL уже запускался ранее:
```bash
docker compose down -v
docker compose up --build
```

## Сервисы:

- **API:** http://localhost:8000

- **Swagger документация:** http://localhost:8000/docs

- **База данных:** localhost:5432

## API Эндпоинты
### Игроки

| Метод   | Эндпоинт                 | Описание                                |
|---------|--------------------------|-----------------------------------------|
| POST    | `/players/`              | Создать игрока                          |
| GET     | `/players/`              | Получить всех игроков                   |
| GET     | `/players/{id}/stats`    | Получить статистику игрока              |
| GET     | `/players/rating/`       | Получить рейтинг игроков                |
| DELETE  | `/players/{id}`          | Удалить игрока (только если нет матчей) |

### Матчи

| Метод   | Эндпоинт                       | Описание               |
|---------|--------------------------------|------------------------|
| POST    | `/matches/`                    | Создать матч           |
| GET     | `/matches/`                    | Получить все матчи     |
| GET     | `/matches/{id}`                | Получить матч по ID    |
| POST    | `/matches/{id}/add_game`       | Добавить гейм (+1)     |
| POST    | `/matches/{id}/reduce_game`    | Убавить гейм (-1)      |
| DELETE  | `/matches/{id}`                | Удалить матч           |


## Примеры запросов (curl)
```bash
# Создать игрока
curl -X POST http://localhost:8000/players/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Женя"}'

# Создать матч
curl -X POST http://localhost:8000/matches/ \
  -H "Content-Type: application/json" \
  -d '{"player1_name": "Женя", "player2_name": "Влад"}'

# Добавить гейм
curl -X POST http://localhost:8000/matches/1/add_game \
  -H "Content-Type: application/json" \
  -d '{"player_name": "Женя", count: 1}'

# Убавить гейм
curl -X POST http://localhost:8000/matches/1/reduce_game \
  -H "Content-Type: application/json" \
  -d '{"player_name": "Влад", count: -1}'

# Получить рейтинг
curl http://localhost:8000/players/rating/

# Получить статистику игрока
curl http://localhost:8000/players/1/stats
```
## Деплой

- **Бекенд:** [Render](https://tennis-score-backend.onrender.com)
- **Фронтенд:** [GitHub Pages](https://ryzhkovevgeniy14-ui.github.io/tennis_score_frontend/)

## Структура проекта
```txt
tennis_score_backend/
├── app/
│   ├── core/          # конфигурация (config.py)
│   ├── db/            # сессии, зависимости
│   ├── models/        # SQLAlchemy модели
│   ├── routers/       # эндпоинты
│   ├── schemas/       # Pydantic схемы
│   ├── services/      # бизнес-логика (матчи, статистика)
│   ├── main.py        # точка входа (lifespan, запуск)
│   └── migrate.py     # вспомогательный скрипт для миграций
├── migrations/        # Alembic миграции
├── docker-compose.yaml
├── Dockerfile
└── requirements.txt
```