from fastapi import APIRouter,Header,Request,HTTPException

from schemas import Signup,Login,Result,RefreshToken,AccessToken,Error
from auth.jwt_auth.jwt_auth import JWTAuth,AccessTokenExpired
from services import AccountsService




router = APIRouter(prefix="/v1")
jwt_object = JWTAuth()
account_service = AccountsService()



@router.post("/signup/")
async def signup(user_data:Signup):
    # Send signup req to `accounts`
    return await account_service.signup(user_data)


@router.post('/login/')
async def login(user_data: Login):
    # send login req to `accounts`
    return await account_service.login(user_data)


@router.post('/refresh/')
async def refresh(token:RefreshToken, user_agent:str=Header(None)):
    # Decode refresh token to generate new access token
    jti,access,refresh = await jwt_object.get_new_tokens(token.token, user_agent)
    return {
        "access_token": access,
        "refresh_token": refresh,
    }

