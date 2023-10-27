import re

from pydantic import BaseModel,Field,validator

from auth.validators import password_validator,username_validator
from auth.jwt_auth.jwt_auth import JWTAuthBackend




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
    username : str
    password : str



class RefreshToken(BaseModel):
    token : str

    @validator("token")
    def token_validator(cls, value):
        splited = value.split(" ")
        assert len(splited) == 2, "prefix missing"
        prefix,token = splited
        assert prefix == JWTAuthBackend.authentication_header_prefix, "invalid prefix"
        assert len(token.split(".")) == 3, "invalid token"
AccessToken = RefreshToken


class Error(BaseModel):
    type : str
    message : str

    class Config:
        extra = "allow"

    def __bool__(self):
        return False


class Result(BaseModel):
    status: bool = Field(True, alias="__status")   #? Should this be True|Error
    data: dict = {}
    error: Error|None

    def __init__(self, __status, **data):
        self.status = __status
        return super().__init__(**data)

    def __bool__(self):
        return self.status

    def model_dump(self, **kwargs):
        excludes = ["error"] if self.error is not None else ["data"]
        return super().model_dump(exclude=excludes, **kwargs)

    class Config:
        extra = "allow"
