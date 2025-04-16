
from pydantic import BaseModel, Field, ConfigDict 
from datetime import datetime
from typing import Optional, List
from beanie import PydanticObjectId

# --- TVProgram Schemas ---

class TVProgramBase(BaseModel):
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    channel_id: str
    tags: Optional[List[str]] = None

class TVProgramCreate(TVProgramBase):
    pass

# --- TVChannel Schemas ---
class TVChannelBase(BaseModel):
    name: str
    country: str

class TVChannelCreate(TVChannelBase):
    pass

# --- Схема для ВИХІДНИХ даних (відповіді API) ---
class TVProgramResponseBase(BaseModel):
    id: PydanticObjectId # ID самої програми
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    tags: Optional[List[str]] = None
    

class TVChannelBasicResponse(TVChannelBase):
    id: PydanticObjectId

    model_config = ConfigDict( 
        json_encoders={
            PydanticObjectId: str
        }
    )

# --- Оновлена TVProgramResponse ---
class TVProgramResponse(TVProgramResponseBase): 
    channel: TVChannelBasicResponse 

    model_config = ConfigDict(
        json_encoders={PydanticObjectId: str},
        json_schema_extra={
            "example": {
                "id": "65f1c3b4d5e6f7a8b9c0d1e2", 
                "title": "Example Program",      
                "description": "An example description.", 
                "start_time": "2024-01-01T12:00:00",     
                "end_time": "2024-01-01T13:00:00",       
                "tags": ["news", "live"],                
                "channel": {                            
                    "id": "65f1c3a0d5e6f7a8b9c0d1e1",
                    "name": "Example Channel",
                    "country": "USA"
                }
            }
        }
    )

# --- Оновлена TVChannelResponse ---
class TVChannelResponse(TVChannelBase):
    id: PydanticObjectId
    programs: List[TVProgramResponse] = []

    model_config = ConfigDict(json_encoders={PydanticObjectId: str})

# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    role: str = 'user'

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    id: PydanticObjectId

    model_config = ConfigDict(
        json_encoders={
            PydanticObjectId: str
        }
    )

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None