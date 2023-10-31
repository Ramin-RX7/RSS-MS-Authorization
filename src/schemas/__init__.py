import re

from pydantic import BaseModel,validator

from .base import *
from auth.validators import password_validator,username_validator
# from auth.jwt_auth.jwt_auth import JWTAuth




class Signup(BaseModel):
    username: str
    password: str
    email: str

    @validator("username")
    def validate_username(cls, value):
        username_validator(value)
        return value

    @validator("password")
    def validate_password(cls, value):
        password_validator(value)
        return value

    @validator("email")
    def email_validator(cls, value):
        assert re.fullmatch(r'\w+@\w+\.\w+', value)  # [a-zA-Z]+[a-zA-Z0-9_\.\-]*@[\w]{2,}\.[a-zA-Z]{2,}
        return value



class Login(BaseModel):
    # username : str
    email : str
    password : str

    @validator("email")
    def email_validator(cls, value):
        assert re.fullmatch(r'\w+@\w+\.\w+', value)
        return value


class JWTPayload(BaseModel):
    email : str
    payload : dict


class AccessToken(BaseModel):
    token : str

    @validator("token")
    def token_validator(cls, value):
        splited = value.split(" ")
        assert len(splited) == 2, "prefix missing"
        prefix,token = splited
        assert prefix == "Token", "invalid prefix"
        assert len(token.split(".")) == 3, "invalid token"
        return value


class RefreshToken(BaseModel):
    token : str

    @validator("token")
    def token_validator(cls, value):
        assert len(value.split(".")) == 3, "invalid token"
        return value
