from fastapi import APIRouter, Depends, HTTPException, status # Додаємо status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm # Додаємо інструменти OAuth2
from sqlalchemy.orm import Session
from database import SessionLocal
import crud
import schemas

import security 
from models import User 
from typing import List 


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")




def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Залежність для отримання поточного користувача ---
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Перевіряє токен і повертає поточного користувача з БД.
    Викликає виняток, якщо токен недійсний або користувач не знайдений.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Перевіряємо токен і отримуємо username
    username = security.verify_token(token, credentials_exception)
    if username is None: 
         raise credentials_exception
    # Отримуємо користувача з БД
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user 


async def get_current_active_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Перевіряє, чи поточний користувач є адміністратором.
    Використовується для захисту адміністративних ендпоінтів.
    """
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted. Admin privileges required."
        )
    return current_user


# --- Роутер для автентифікації ---
auth_router = APIRouter(
    prefix="/auth", 
    tags=["Authentication"] 
)

@auth_router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Реєструє нового користувача.
    За замовчуванням створюється з роллю 'user'.
    """
    # Перевірка, чи користувач вже існує
    db_user = crud.get_user_by_username(db, username=user_in.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    # Створюємо користувача
    created_user = crud.create_user(db=db, user=user_in)
    return created_user # Повертаємо дані створеного користувача (без пароля)

@auth_router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Автентифікує користувача та повертає JWT токен доступу.
    Використовує стандартний `OAuth2PasswordRequestForm` для отримання username/password.
    """
    user = crud.get_user_by_username(db, username=form_data.username)
    # Перевіряємо, чи існує користувач і чи правильний пароль
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Створюємо токен доступу
    access_token = security.create_access_token(
        data={"sub": user.username} # 'sub' - стандартне поле для ідентифікатора користувача в JWT
    )
    # Повертаємо токен
    return {"access_token": access_token, "token_type": "bearer"}

# --- Основний роутер програми ---
app_router = APIRouter() 


@app_router.post("/programs/", response_model=schemas.TVProgramResponse, status_code=status.HTTP_201_CREATED)
def create_program(
    program: schemas.TVProgramCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin_user)
):
    return crud.create_tv_program(db, program)

@app_router.put("/programs/{program_id}", response_model=schemas.TVProgramResponse)
def update_program(
    program_id: int,
    updated_program: schemas.TVProgramCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin_user)
):
    return crud.update_tv_program(db, program_id, updated_program)

@app_router.delete("/programs/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin_user)
):
     result = crud.delete_tv_program(db, program_id)
     return None 


# --- Публічні ендпоінти ---

@app_router.get("/programs/", response_model=list[schemas.TVProgramResponse])
def get_all_programs(db: Session = Depends(get_db)):
    return crud.get_all_tv_programs(db)
@app_router.get("/programs/{program_id}", response_model=schemas.TVProgramResponse)
def get_program(program_id: int, db: Session = Depends(get_db)):
    return crud.get_tv_program(db, program_id)


@app_router.get("/channels/", response_model=List[schemas.TVChannelBasicResponse]) 
def read_channels(db: Session = Depends(get_db)):
    """
    Get a list of all TV channels (basic info only).
    """
    channels = crud.get_all_channels(db)
    return channels 

@app_router.get("/channels/{channel_id}", response_model=schemas.TVChannelResponse) 
def read_channel_with_programs(channel_id: int, db: Session = Depends(get_db)):
    """
    Get a specific TV channel by its ID, including all its associated programs.
    """
    channel = crud.get_channel_with_programs(db, channel_id=channel_id)
    return channel



# Додамо ендпоінт для перевірки поточного користувача
@app_router.get("/users/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Повертає дані поточного автентифікованого користувача.
    """
    return current_user
