from fastapi import HTTPException



class PermissionDenied(HTTPException):
    def __init__(self, message=""):
        return super().__init__(403, message)


class ParseError(Exception):
    ...


class AccessTokenExpired(Exception):
    ...
