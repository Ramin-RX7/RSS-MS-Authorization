from typing import Any
from fastapi import APIRouter,Header,Depends

from schemas import Signup,Login,RefreshToken,JWTPayload
from auth.jwt_auth.jwt_auth import JWTHandler
from schemas.base import Result,Response
from services import AccountsService




router = APIRouter(prefix="/v1")
jwt_object = JWTHandler()
account_service = AccountsService()



@router.post("/signup/")
async def signup(user_data:Signup) -> dict[str, Any]:
    """signup route which validate user data and send it to "accounts" service

    Args:
    -----
    - user_data (`Signup`): _Signup data sent by user_

    Returns:
    --------
    `dict[str, Any]`: (as of now) returns the response of "accounts" service
    """
    resp = await account_service.signup(user_data)
    if resp:
        ...
    return resp.model_dump()


@router.post('/login/')
async def login(user_data: Login, user_agent:str=Header()):
    """login route which validate user data via sending request to "accounts" service

    Args:
    -----
    - user_data `(Login)`: _user login data_
    - user_agent `(str, optional)`: _user-agent http header_

    Returns:
    --------
    `_type_`: _description_
    """
    res = await account_service.login(user_data)
    if res:
        user_email = res["data"]["email"]
        access,refresh = await jwt_object.login(user_email, user_agent)
        return {   #? make this Result?
            "access_token": access,
            "refresh_token": refresh
        }
    # error occured
    return res


@router.post('/refresh/')
async def refresh(token:RefreshToken, user_agent:str=Header(None)) -> dict[str, str]:
    """Re-login route which is used when receiving 401 status code which means access\
    token is expired and refresh token has to be used to retrieve new tokens

    Args:
    -----
    - token `(RefreshToken)`: _Refresh token object (token field with validation)_
    - user_agent `(str, optional)`: _user-agent http header_

    Returns:
    --------
    `dict[str, str]`: _description_
    """
    access,refresh = await jwt_object.refresh(token.token, user_agent)
    return {      #? make this Result?
        "access_token": access,
        "refresh_token": refresh,
    }


@router.post('/logout',)
async def logout(jwt:JWTPayload=Depends(jwt_object)):
    """(requires jwt) logout

    Returns:
    --------
    `Result`: empty Result object
    """
    await jwt_object.logout(jwt.email, jwt.payload.get("jti"))
    return Response()
