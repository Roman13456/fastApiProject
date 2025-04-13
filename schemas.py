from pydantic import BaseModel, Field # Додаємо Field для пароля
from datetime import datetime
from typing import Optional, List # Import List

class TVProgramBase(BaseModel):
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    channel_id: int

class TVProgramCreate(TVProgramBase):
    pass  # Використовується при створенні (POST-запит)

class TVProgramResponse(TVProgramBase):
    id: int  # Додаємо поле, яке приходить із бази

    class Config:
        orm_mode = True 

class TVChannelBase(BaseModel):
    name: str
    country: str

class TVChannelCreate(TVChannelBase):
    pass

# --- Schema for listing channels WITHOUT programs ---
class TVChannelBasicResponse(TVChannelBase):
    id: int

    class Config:
        orm_mode = True

class TVChannelResponse(TVChannelBase):
    id: int
    programs: List[TVProgramResponse] = [] # Add this line

    class Config:
        orm_mode = True # Changed from from_attributes = True


# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    role: str = 'user' # Роль за замовчуванням

class UserCreate(UserBase):
    password: str = Field(..., min_length=8) 

class UserResponse(UserBase): # Схема для повернення даних користувача (БЕЗ пароля)
    id: int

    class Config:
        orm_mode = True 

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str 

class TokenData(BaseModel):
    username: Optional[str] = None