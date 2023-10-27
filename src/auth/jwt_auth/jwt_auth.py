
from fastapi import Request,Depends,HTTPException

import jwt

from .utils import decode_jwt,generate_tokens
from .exceptions import *





class JWTAuth:
    def __init__(self):
        self.auth = JWTAuthBackend()

    async def __call__(self, request:Request):
        try:
            username = self.auth.authenticate(request)
            # user = await get_user(username)
            return True
        except Exception as e:
            print(str(e))
            raise HTTPException(403, "error occured!")
        else:
            if user is None:
                raise HTTPException(403,"User not found")
            return user

    async def get_new_access(self, refresh_token, user_agent):
        jti, access, refresh = await self.auth.get_new_tokens(refresh_token, user_agent)
        return {
            "access_token": access,
            "refresh_token": refresh
        }



class JWTAuthBackend:
    authentication_header_prefix = 'Token'
    authentication_header_name = 'Authorization'

    def authenticate(self, access_token, user_agent):
        payload = self._validate_access_token(access_token)
        user = self._get_user(payload)
        jti = payload.get('jti')
        # self._validate_cache_data(user, jti, user_agent)
        return user#, payload


    def _get_user_agent(self, headers):
        user_agent = headers.get("user-agent")
        if user_agent is None:
            raise PermissionDenied('user-agent header is not provided')
        return user_agent

    def _get_access_token(self, request):
        auth_header = request.headers.get(self.authentication_header_name)
        if not auth_header:
            raise PermissionDenied("No access token")
        full_token = auth_header.split(' ')
        if (len(full_token) != 2) or (full_token[0] != self.authentication_header_prefix):
            raise PermissionDenied('Token prefix missing')
        return full_token[1]

    def _validate_access_token(self, token):
        try:
            return decode_jwt(token)
        except jwt.ExpiredSignatureError:
            raise AccessTokenExpired('Access token expired') from None
        except jwt.DecodeError:
            raise
            raise ParseError("invalid access token")

    def _get_user(self, payload):
        username = payload.get("username")
        return username

    def _validate_cache_data(self, user, jti, agent):
        user_redis_jti = auth_cache.get(f"{user.id}|{jti}")
        if user_redis_jti is None:
            raise PermissionDenied('Not Found in cache, login again.')
        if user_redis_jti != agent:
            raise PermissionDenied('Invalid refresh token, please login again.')




    def get_new_tokens(self, refresh_token, user_agent):
        payload = self._get_refresh_payload(refresh_token)
        user = self._get_user(payload)
        jti = payload.get('jti')
        self._validate_cache_data(user, jti, user_agent)
        self.deprecate_refresh_token(user, jti, user_agent)
        return generate_tokens(user.username)



    def _get_refresh_token(self, request):
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
            raise ParseError("invalid refresh token")

    def deprecate_refresh_token(self, user, jti, user_agent):
        auth_cache.delete(f"{user.id}|{jti}")


