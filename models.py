from datetime import datetime
from typing import Optional, List
from beanie import Document, Link, Indexed 
from pydantic import Field
from pymongo import IndexModel, ASCENDING

# --- Модель Каналу ---
class TVChannel(Document):
    name: Indexed(str, unique=True) 
    country: str

    class Settings:
        name = "channels"

# --- Модель Користувача ---
class User(Document):
    username: Indexed(str, unique=True)
    password_hash: str
    role: str = Field(default='user')

    class Settings:
        name = "users"

# --- Модель Програми ---
class TVProgram(Document):
    title: str 
    description: str
    start_time: datetime 
    end_time: datetime
    channel: Link[TVChannel]
    tags: Optional[List[str]] = None

    class Settings:
        name = "programs"
        indexes = [
            IndexModel([("title", ASCENDING)], name="title_asc_index"),
            IndexModel([("start_time", ASCENDING)], name="start_time_asc_index"),
        ]