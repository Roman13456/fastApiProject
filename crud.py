from sqlalchemy.orm import Session, joinedload 
from models import TVProgram, TVChannel, User
from schemas import TVProgramCreate, TVProgramResponse, TVChannelCreate, TVChannelResponse, UserCreate, UserResponse
from fastapi import HTTPException
# Додаємо імпорт функції хешування
from typing import Optional
from security import hash_password


def create_tv_program(db: Session, program: TVProgramCreate) -> TVProgramResponse:
    # Перевіряємо, чи існує канал з таким channel_id
    channel = db.query(TVChannel).filter(TVChannel.id == program.channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Канал не знайдений")

    db_program = TVProgram(**program.dict())
    db.add(db_program)
    db.commit()
    db.refresh(db_program)
    return db_program

def get_tv_program(db: Session, program_id: int) -> TVProgramResponse:
    program = db.query(TVProgram).filter(TVProgram.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Програма не знайдена")
    return program

def get_all_tv_programs(db: Session):
    return db.query(TVProgram).all()


def update_tv_program(db: Session, program_id: int, updated_program: TVProgramCreate) -> TVProgramResponse:
    program = db.query(TVProgram).filter(TVProgram.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Програма не знайдена")

    for key, value in updated_program.dict().items():
        setattr(program, key, value)  # Оновлюємо кожне поле

    db.commit()
    db.refresh(program)
    return program


def delete_tv_program(db: Session, program_id: int):
    program = db.query(TVProgram).filter(TVProgram.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Програма не знайдена")

    db.delete(program)
    db.commit()
    return {"message": "Програма видалена"}

def get_all_channels(db: Session):
    """Fetches all TV Channels without their programs."""
    return db.query(TVChannel).all()

def get_channel_with_programs(db: Session, channel_id: int):
    """Fetches a single TV Channel by ID, including its associated programs."""
    # Use joinedload to efficiently load programs in the same query
    channel = db.query(TVChannel).options(
        joinedload(TVChannel.programs)
    ).filter(TVChannel.id == channel_id).first()

    if not channel:
        raise HTTPException(status_code=404, detail="Канал не знайдений")
    return channel


# --- NEW User CRUD functions ---

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Отримує користувача з БД за ім'ям."""
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate) -> User:
    """Створює нового користувача в БД."""
    # Хешуємо пароль перед збереженням
    hashed_password = hash_password(user.password)
    # Створюємо об'єкт моделі User, не передаючи оригінальний пароль
    db_user = User(
        username=user.username,
        password_hash=hashed_password,
        role=user.role or 'user' # Встановлюємо роль (або 'user' за замовчуванням)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

