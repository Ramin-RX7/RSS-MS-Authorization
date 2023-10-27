from fastapi import APIRouter,Header,Request,HTTPException

from schemas import Signup,Login,Result,RefreshToken,AccessToken,Error
from auth.jwt_auth.jwt_auth import JWTAuth,AccessTokenExpired
from services import AccountsService




router = APIRouter()
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
async def refresh(token: RefreshToken, user_agent: str = Header(None)):
    # Decode refresh token to generate new access token
    await jwt_object.refresh(token.token, user_agent)


async def authenticate(request:Request, token:AccessToken):
    try:
        user = jwt_object(request)
    except AccessTokenExpired as e:
        return Result(False).model_dump()
    except Exception as e:
        return Result(False, error={
            "type": type(e).__name__,
            "message": str(e)
        })
    return Result().model_dump()
