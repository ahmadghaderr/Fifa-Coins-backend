from pydantic import BaseModel, EmailStr, Field
from typing import Literal , Optional
from uuid import uuid4

class SignupData(BaseModel):
    username: str
    email: EmailStr
    password: str
    phone: str
    role: Literal["buyer", "admin"]

class UserInDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    username: str
    email: EmailStr
    hashed_password: str
    phone: str 
    role: Literal["buyer", "admin"]

class LoginData(BaseModel):
    email: EmailStr
    password: str
    
class UpdateUserData(BaseModel):
    username:(Optional)[str]
    email:(Optional)[EmailStr]
    password:(Optional)[str]
    phone:(Optional)[str]
