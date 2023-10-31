from fastapi import Request,HTTPException

import jwt

from schemas import Result
from services import RedisService
from .utils import (
    decode_jwt,
    _generate_access_token,
    _generate_payload,
    _generate_refresh_token,
    encode_payload,
)
from .exceptions import PermissionDenied





class JWTAuth:
    """JWT authentication class

    generates and validates access/refresh tokens of users.

    Attributes:
    -----------
    - auth_cache (`RedisService`): Used to interact with Redis to validate token request

    Methods:
    --------
    - sync: `generate_tokens`,
    - async: `get_new_tokens`,

    Usage:
    ------
    ```python
    jwt_object = JWTAuth()

    @app.get("/some-protected-route/")
    async def my_protected_route(username:str=Depends(jwt_object))
        ...
    ```
    """
    authentication_header_prefix = 'Token'
    authentication_header_name = 'Authorization'

    def __init__(self):
        self.auth_cache = RedisService()

    async def __call__(self, request:Request) -> Result:
        await self._authenticate(request)
        # user = await get_user(username)
        return Result()

    async def _authenticate(self, request:Request):
        """Used for complete validation of access token

        Steps:
        - validate given header of access token
        - validate given value of access token
        - check jti still exists in redis

        Args:
        -----
        - request `(Request)`: _Received request from user_

        Returns:
        --------
        `str`: _username of request user_
        """
        access_token = self._get_access_token(request)
        payload = self._validate_access_token(access_token)
        user = await self._get_user(payload)
        jti = payload.get('jti')
        user_agent = self._get_user_agent(request.headers)
        await self._validate_cache_data(user, jti, user_agent)
        return user#, payload

    async def get_new_tokens(self, refresh_token:str, user_agent:str):
        """Must be used when Http:401 status code is raised
        (which means access token is expired so refresh token must be used)

        Steps:
        ------
        - validate refresh token
        - validate jti with redis
        - deprecate jti saved in redis
        - generate new tokens (using self.generate_tokens)

        Args:
        -----
        - refresh_token `(str)`: _Latest generated refresh token of the user_
        - user_agent `(str)`: _User-agent http header_

        Returns:
        --------
        `tuple[str, str, str]`: returns tuple of: jti, access token, refresh token
        """
        payload = self._get_refresh_payload(refresh_token)
        username = await self._get_user(payload)
        jti = payload.get('jti')
        await self._validate_cache_data(username, jti, user_agent)
        await self._deprecate_refresh_token(username, jti, user_agent)
        return self.generate_tokens(username)

    def generate_tokens(self, username:str) -> tuple[str,str,str]:
        """Used to generate tokens for user manually

        Normally it is called alone only when user logins with username and password.

        Args:
        -----
        - username `(str)`: _username of the user_

        Returns:
        --------
        `tuple[str,str,str]`: returns tuple of jti, access token, refresh token
        """
        base_payload = _generate_payload(username)
        access_payload = _generate_access_token(base_payload)
        refresh_payload = _generate_refresh_token(base_payload)
        return (base_payload["jti"], encode_payload(access_payload), encode_payload(refresh_payload))



    def _get_user_agent(self, headers):
        """Get user agent from request headers

        Args:
        -----
        - headers `()`: headers retrieved from request

        Raises:
        -------
        PermissionDenied: raised when user-agent header is not provided in headers

        Returns:
        --------
        `str`: user agent header
        """
        user_agent = headers.get("user-agent")
        if user_agent is None:
            raise PermissionDenied('user-agent header is not provided')
        return user_agent

    def _get_access_token(self, request):
        """Retrieves access token from authorization headers and validates the prefix

        Args:
        -----
        - request `(Request)`: _request send by user_

        Raises:
        - PermissionDenied: when `self.authentication_header_name` is not given
        - PermissionDenied: when token prefix (self.authentication_header_prefix) is missing.

        Returns:
        --------
        `str`: access token
        """
        auth_header = request.headers.get(self.authentication_header_name)
        if not auth_header:
            raise PermissionDenied("No access token")
        full_token = auth_header.split(' ')
        if (len(full_token) != 2) or (full_token[0] != self.authentication_header_prefix):
            raise PermissionDenied('Token prefix missing')
        return full_token[1]

    def _validate_access_token(self, token):
        """Validates access token with decoding it

        Args:
        -----
        - token `(str)`: _token retrievd from auth headers_

        Raises:
        - HTTPException (401): _When access token is expired_
        - HTTPException (403): _When invalid access token is given (can not be decoded)_

        Returns:
        --------
        `dict`: payload saved in the access token
        """
        try:
            return decode_jwt(token)
        except jwt.ExpiredSignatureError:
            raise HTTPException(401,'Access token expired') from None
        except jwt.DecodeError:
            raise HTTPException(403, "invalid access token")

    async def _get_user(self, payload):
        """Gets username from token retrieved payload

        Args:
        -----
        - payload `(dict)`: _decoded payload from a token_

        Returns:
        --------
        `str`: returns username retrieved from payload
        """
        username = payload.get("username")
        return username

    async def _validate_cache_data(self, username:str, jti:str, user_agent:str):
        """Checks if redis contains data of the user

        Args:
        -----
        - user `(str)`: _username of user_
        - jti `(str)`: _jti taken from token payload_
        - agent `(str)`: _request user-agent header value_

        Raises:
        - PermissionDenied: _when jti is not found in redis_
        - PermissionDenied: _when refresh token is taken from another device/browser_
        """
        user_redis_jti = await self.auth_cache.get(f"{username}|{jti}")
        if user_redis_jti is None:
            raise PermissionDenied('Not Found in cache, login again.')
        if user_redis_jti != user_agent:
            raise PermissionDenied('Invalid refresh token, please login again.')

    def _get_refresh_payload(self, token:str):
        """Retrieves decoded payload of refresh

        Args:
        -----
        - token `(str)`: _user given refresh token_

        Raises:
        - PermissionDenied: _When refresh token is expired_
        - HTTPException: _When refresh token is not decodeable_

        Returns:
        --------
        `dict`: payload of the token
        """
        try:
            return decode_jwt(token)
        except jwt.ExpiredSignatureError:
            raise PermissionDenied(
                'Expired refresh token, please login again.') from None
        except jwt.DecodeError:
            raise
            raise HTTPException(403,"invalid refresh token")

    async def _deprecate_refresh_token(self, username:str, jti:str, user_agent:str):
        """Removes refresh token from redis cache"""
        await self.auth_cache.delete(f"{username}|{jti}")

    async def _save_cache(self, username:str, jti:str, user_agent:str):
        """Saves new data to redis cache"""
        key = f"{username}|{jti}"
        value = f"{user_agent}"
        await self.auth_cache.set(key,value)
