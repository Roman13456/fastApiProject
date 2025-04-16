import os
import motor.motor_asyncio # Асинхронний драйвер MongoDB
from beanie import init_beanie
from dotenv import load_dotenv
from typing import List, Type # Для списку моделей

# Імпортуємо майбутні моделі (поки що вони не визначені, але імпорт потрібен для init_beanie)
# Ми створимо їх у наступному кроці
from models import User, TVChannel, TVProgram # Припустимо, що моделі будуть у models.py

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI не встановлено в .env")
if not DATABASE_NAME:
    raise ValueError("DATABASE_NAME не встановлено в .env")

DOCUMENT_MODELS: List[Type["Document"]] = [User, TVChannel, TVProgram] # type: ignore # Поки що ігноруємо помилку типів

async def init_db_connection():
    """
    Ініціалізує підключення до MongoDB та Beanie.
    Викликається при старті FastAPI.
    """
    print(f"Підключення до MongoDB Atlas: {MONGODB_URI[:20]}... База даних: {DATABASE_NAME}") # Логування для перевірки
    try:
        # Створюємо асинхронного клієнта Motor
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)

        # Перевірка з'єднання 
        await client.admin.command('ping')
        print("Ping до MongoDB успішний!")

        # Ініціалізуємо Beanie з клієнтом, базою даних та списком моделей
        await init_beanie(
            database=client[DATABASE_NAME], # Доступ до бази даних через клієнт
            document_models=DOCUMENT_MODELS
        )
        print(f"Beanie ініціалізовано для бази даних '{DATABASE_NAME}' з моделями: {[model.__name__ for model in DOCUMENT_MODELS]}")
        # --- Додавання початкових даних (канали) ---
        print("Перевірка наявності початкових каналів...")
        channel_count = await TVChannel.count() # Перевіряємо кількість документів у колекції
        if channel_count == 0:
            print("Колекція каналів порожня. Додавання початкових каналів...")
            initial_channels = [
                TVChannel(name="Discovery", country="USA"),
                TVChannel(name="National Geographic", country="USA"),
                TVChannel(name="BBC News", country="UK"),
                TVChannel(name="CNN", country="USA")
            ]
            # Використовуємо insert_many для додавання списку документів
            await TVChannel.insert_many(initial_channels)
            print(f"Додано {len(initial_channels)} початкових каналів.")
        else:
            print(f"У колекції вже є {channel_count} каналів. Додавання пропущено.")

    except Exception as e:
        print(f"ПОМИЛКА: Не вдалося підключитися до MongoDB або ініціалізувати Beanie: {e}")
        raise 

