from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Імпортуємо роутери
from routes import auth_router, app_router
from database import init_db_connection

app = FastAPI()

# --- CORS Middleware ---
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Реєструємо подію startup для ініціалізації Beanie ---
@app.on_event("startup")
async def startup_db_client():
    """
    Асинхронна функція, що викликається при старті FastAPI.
    Ініціалізує підключення до MongoDB.
    """
    await init_db_connection()

# --- Включаємо роутери ---
app.include_router(auth_router)
app.include_router(app_router)

@app.get("/")
def root():
    return {"message": "API телепрограми працює (з MongoDB)!"}


