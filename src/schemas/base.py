from pydantic import BaseModel,Field



class Error(BaseModel):
    type : str
    message : str

    class Config:
        extra = "allow"

    def __bool__(self):
        return False


class Result(BaseModel):
    status: bool = Field(True)   #? Should this be True|Error
    data: dict = {}
    error: Error|None = None

    def __init__(self, __status=True, **data):
        # self.status = __status
        return super().__init__(status=__status, **data)

    def __bool__(self):
        return self.status

    def model_dump(self, **kwargs):
        excludes = ["error"] if (self.error is None) else ["data"]
        if "exclude" in kwargs:
            kwargs.pop("exclude")
        return super().model_dump(exclude=excludes, **kwargs)

    @classmethod
    def resolve_exception(cls, exc:Exception):
        return cls(False, error=Error(
            type=type(exc).__name__,
            message=str(exc)
        ))

    @classmethod
    def resolve_error(cls, error_class):
        return cls(False, error=error_class())

    # Context manager to handle errors occured in it's body
    #   (same as exception handler in AccountsService._request)


    class Config:
        extra = "allow"


class Response(Result):
    http_code : int
