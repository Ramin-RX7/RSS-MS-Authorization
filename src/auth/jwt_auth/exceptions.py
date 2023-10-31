from fastapi import HTTPException



class PermissionDenied(HTTPException):
    """Permission denied is an http error with raising 403 stauts code
    """
    def __init__(self, message=""):
        return super().__init__(403, message)
