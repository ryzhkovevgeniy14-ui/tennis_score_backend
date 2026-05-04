from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import players, matches


app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # потом можно сузить до фронта
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(players.router)
app.include_router(matches.router)


@app.get("/")
async def root():
    return {'message': 'Welcome to the Tennis Score API!'}