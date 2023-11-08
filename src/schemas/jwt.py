from bson import ObjectId
from pydantic import BaseModel, field_serializer, field_validator


class JWTPayload(BaseModel):
    id : ObjectId
    payload : dict

    class Config:
        extra = "ignore"
        arbitrary_types_allowed=True

    @field_validator("id",mode="before")
    def id_validator(cls, value):
        if type(value)==str:
            return ObjectId(value)
        return value

    @field_serializer('id')
    def id_serializer(self, id, _info):
        return str(id)
