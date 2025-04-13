from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Import CORS
# from sqlalchemy import text
# Імпортуємо роутери з routes
from routes import auth_router, app_router # Замість import routes
from database import SessionLocal, Base # Base може знадобитися для створення таблиць, якщо не через Alembic
from models import TVChannel # Потрібен для init_db


app = FastAPI()

# --- Add CORS Middleware ---
origins = [
    "http://localhost:5173", # Default Vite port
    "http://localhost:3000", # Default CRA port
    # Add your deployed frontend URL here if applicable
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Allows specific origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"], # Allows all headers (including Authorization)
)

def init_db():
    db = SessionLocal()

    if db.query(TVChannel).count() == 0:  # Якщо база пуста
        channels = [
            TVChannel(name="Discovery", country="USA"),
            TVChannel(name="National Geographic", country="USA"),
            TVChannel(name="BBC News", country="UK"),
            TVChannel(name="CNN", country="USA")
        ]
        db.add_all(channels)
        db.commit()
    db.close()

@app.on_event("startup") 
def startup():
    init_db()

# --- Включаємо роутери ---
app.include_router(auth_router) # Додаємо роутер автентифікації
app.include_router(app_router)  # Додаємо основний роутер програми

@app.get("/")
def root():
    return {"message": "API телепрограми працює!"}


