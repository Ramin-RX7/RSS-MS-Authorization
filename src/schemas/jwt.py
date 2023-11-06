from bson import ObjectId
from pydantic import BaseModel


class JWTPayload(BaseModel):
    id : ObjectId
    payload : dict

    class Config:
        arbitrary_types_allowed = True
        extra = "ignore"
