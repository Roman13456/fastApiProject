# security.py
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv() 

# --- Налаштування ---
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30))

if not JWT_SECRET_KEY:
    raise ValueError("Не встановлено JWT_SECRET_KEY в .env файлі")

# --- Хешування паролів ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Перевіряє, чи збігається звичайний пароль з хешованим."""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """Хешує пароль для збереження."""
    return pwd_context.hash(password)

# --- Робота з JWT ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Створює новий JWT токен доступу."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception) -> Optional[str]:
    """
    Перевіряє JWT токен.
    Повертає ім'я користувача (sub) якщо токен валідний, інакше викликає виняток.
    """
    try:
        # Декодуємо токен
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        # Якщо сталася помилка декодування або підпис невірний
        raise credentials_exception
    except Exception as e:
        # Інші можливі помилки
        print(f"Помилка верифікації токена: {e}") 
        raise credentials_exception