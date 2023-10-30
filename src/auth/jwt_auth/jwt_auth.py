from fastapi import Request,HTTPException

import jwt

from schemas import Result
from services import RedisService
from .utils import decode_jwt,generate_tokens
from .exceptions import *





class JWTAuth:
    authentication_header_prefix = 'Token'
    authentication_header_name = 'Authorization'

    def __init__(self):
        self.auth_cache = RedisService()

    async def __call__(self, request:Request):
        username = await self.authenticate(request)
        # user = await get_user(username)
        return Result()

    async def authenticate(self, request):
        access_token = self._get_access_token(request)
        payload = self._validate_access_token(access_token)
        user = self._get_user(payload)
        jti = payload.get('jti')
        user_agent = self._get_user_agent(request.headers)
        self._validate_cache_data(user, jti, user_agent)
        return user#, payload

    async def get_new_tokens(self, refresh_token, user_agent):
        print(type(refresh_token))
        payload = self._get_refresh_payload(refresh_token)
        username = self._get_user(payload)
        jti = payload.get('jti')
        await self._validate_cache_data(username, jti, user_agent)
        await self._deprecate_refresh_token(username, jti, user_agent)
        return generate_tokens(username)


    async def _get_user_agent(self, headers):
        user_agent = headers.get("user-agent")
        if user_agent is None:
            raise PermissionDenied('user-agent header is not provided')
        return user_agent

    async def _get_access_token(self, request):
        auth_header = request.headers.get(self.authentication_header_name)
        if not auth_header:
            raise PermissionDenied("No access token")
        full_token = auth_header.split(' ')
        if (len(full_token) != 2) or (full_token[0] != self.authentication_header_prefix):
            raise PermissionDenied('Token prefix missing')
        return full_token[1]

    async def _validate_access_token(self, token):
        try:
            return decode_jwt(token)
        except jwt.ExpiredSignatureError:
            raise HTTPException(401,'Access token expired') from None
        except jwt.DecodeError:
            raise HTTPException(403, "invalid access token")

    def _get_user(self, payload):
        username = payload.get("username")
        return username

    async def _validate_cache_data(self, user, jti, agent):
        user_redis_jti = await self.auth_cache.get(f"{user.id}|{jti}")
        if user_redis_jti is None:
            raise PermissionDenied('Not Found in cache, login again.')
        if user_redis_jti != agent:
            raise PermissionDenied('Invalid refresh token, please login again.')


    async def _get_refresh_token(self, request):
        token = request.data.get("refresh_token")
        if token is None:
            raise PermissionDenied('Authentication credentials were not provided.')
        return token

    def _get_refresh_payload(self, token):
        try:
            return decode_jwt(token)
        except jwt.ExpiredSignatureError:
            raise PermissionDenied(
                'Expired refresh token, please login again.') from None
        except jwt.DecodeError:
            raise
            raise HTTPException(403,"invalid refresh token")

    async def _deprecate_refresh_token(self, user, jti, user_agent):
        await self.auth_cache.delete(f"{user.id}|{jti}")
