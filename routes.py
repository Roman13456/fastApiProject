
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import crud
import schemas
from models import User, TVProgram, TVChannel 
from beanie import PydanticObjectId
import security
from typing import List

# --- Налаштування OAuth2 ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


# --- Залежність для отримання поточного користувача ---
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User: 
    """
    Перевіряє токен і повертає поточного користувача з MongoDB.
    Викликає виняток, якщо токен недійсний або користувач не знайдений.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = security.verify_token(token, credentials_exception)
    if username is None:
         raise credentials_exception
    user = await crud.get_user_by_username(username=username)
    if user is None:
        raise credentials_exception
    return user

# --- Залежність для перевірки адміна ---
async def get_current_active_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Перевіряє, чи поточний користувач є адміністратором.
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
async def register_user(user_in: schemas.UserCreate): 
    """Реєструє нового користувача."""
    db_user = await crud.get_user_by_username(username=user_in.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    # Викликаємо async create_user
    created_user = await crud.create_user(user_data=user_in)
    return created_user

@auth_router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()): 
    """Автентифікує користувача та повертає JWT токен."""
    user = await crud.get_user_by_username(username=form_data.username)
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Основний роутер програми ---
app_router = APIRouter()

# --- Program Routes ---

@app_router.post("/programs/", response_model=schemas.TVProgramResponse, status_code=status.HTTP_201_CREATED)
async def create_program_endpoint( 
    program: schemas.TVProgramCreate,
    current_admin: User = Depends(get_current_active_admin_user)
):
    """Створює нову телепрограму (тільки для адмінів)."""
    created_program = await crud.create_tv_program(program_data=program)
    if created_program is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Channel with id {program.channel_id} not found"
        )
    await created_program.fetch_link(TVProgram.channel)
    return created_program

@app_router.get("/programs/", response_model=List[schemas.TVProgramResponse])
async def get_all_programs_endpoint(): 
    """Отримує список всіх телепрограм."""
    return await crud.get_all_tv_programs()

@app_router.get("/programs/{program_id}", response_model=schemas.TVProgramResponse)
async def get_program_endpoint(program_id: PydanticObjectId): 
    """Отримує конкретну телепрограму за її ID."""
    program = await crud.get_tv_program(program_id=program_id)
    if program is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")
    return program

@app_router.put("/programs/{program_id}", response_model=schemas.TVProgramResponse)
async def update_program_endpoint(
    program_id: PydanticObjectId, 
    updated_program_data: schemas.TVProgramCreate,
    current_admin: User = Depends(get_current_active_admin_user)
):
    """Оновлює телепрограму за ID (тільки для адмінів)."""
    updated_program = await crud.update_tv_program(
        program_id=program_id,
        updated_data=updated_program_data
    )
    if updated_program is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program or associated new Channel not found")
    return updated_program

@app_router.delete("/programs/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_program_endpoint(
    program_id: PydanticObjectId, 
    current_admin: User = Depends(get_current_active_admin_user)
):
    """Видаляє телепрограму за ID (тільки для адмінів)."""
    deleted = await crud.delete_tv_program(program_id=program_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")
    return None

# --- Channel Routes ---

@app_router.get("/channels/", response_model=List[schemas.TVChannelBasicResponse])
async def read_channels_endpoint(): 
    """Отримує список всіх телеканалів (базова інформація)."""
    return await crud.get_all_channels()

@app_router.get("/channels/{channel_id}", response_model=schemas.TVChannelResponse)
async def read_channel_with_programs_endpoint(channel_id: PydanticObjectId): 
    """Отримує канал за ID разом з його програмами."""
    result  = await crud.get_channel_and_programs(channel_id=channel_id)
    if result  is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    channel, programs = result
    channel_data = channel.model_dump() 
    channel_data["programs"] = programs 
    return channel_data

# --- User Routes ---

@app_router.get("/users/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Повертає дані поточного автентифікованого користувача."""
    return current_user
