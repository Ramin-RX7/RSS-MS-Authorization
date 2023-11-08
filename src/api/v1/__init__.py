from fastapi import APIRouter,Header,Depends
from fastapi.responses import JSONResponse

from schemas import Signup,Login,RefreshToken,JWTPayload
from auth.jwt_auth.jwt_auth import JWTHandler
from schemas.base import Result
from services import AccountsService




router = APIRouter(prefix="/v1")
jwt_object = JWTHandler()
account_service = AccountsService()




@router.post("/signup/")
async def signup(user_data:Signup):
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
        return JSONResponse(resp.data, 201)
    return JSONResponse(resp.error, 400 if resp.status is False  else 500)


@router.post('/login/')
async def login(user_data: Login, user_agent:str=Header()):
    """login route which validate user data via sending request to "accounts" service

    Args:
    -----
    - user_data `(Login)`: _user login data_
    - user_agent `(str, optional)`: _user-agent http header_

    Returns:
    --------
    `JsonResponse` (200): _If given credentials are correct, access_token and refresh_token will be returned_
    """
    res = await account_service.login(user_data)
    if res:
        user = res.data["user"]
        tokens = await jwt_object.login(user["id"], user_agent)
        return {
            "access_token": tokens["access"],
            "refresh_token": tokens["refresh"]
        }
    return JSONResponse(res.error, 400 if res.status is False  else 500)


@router.post('/refresh/')
async def refresh(token:RefreshToken, user_agent:str=Header(None)):
    """Re-login route which is used when receiving 401 status code which means access\
    token is expired and refresh token has to be used to retrieve new tokens

    Args:
    -----
    - token `(RefreshToken)`: _Refresh token object (token field with validation)_
    - user_agent `(str, optional)`: _user-agent http header_

    Returns:
    --------
    `JsonResponse` (201): _If token and user_agent are correct, access_token and refresh_token will be returned_
    """
    tokens = await jwt_object.refresh(token.token, user_agent)
    return JSONResponse({
        "access_token": tokens["access"],
        "refresh_token": tokens["refresh"],
    }, 201)


@router.post('/logout',)
async def logout(jwt:JWTPayload=Depends(jwt_object)):
    """(requires jwt) logout

    Returns:
    --------
    `Result`: empty Result object
    """
    await jwt_object.logout(jwt.id, jwt.payload.get("jti"))
    return JSONResponse(Result().model_dump(), 202)
