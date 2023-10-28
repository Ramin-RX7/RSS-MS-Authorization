import httpx

from config import SETTINGS
from schemas import Signup,Login,Result



class AccountsService:
    def __init__(self, base_url=None, api_key=None):
        self.base_url = base_url or SETTINGS.ACCOUNTS_SERVICE_BASE_URL
        self.api_key = api_key or SETTINGS.ACCOUNTS_SERVICE_API_KEY

    async def login(self, data:Login) -> Result:
        resp = await self._request("v1/login", data.model_dump())
        return resp

    async def signup(self, data:Signup) -> Result:
        resp = await self._request("v1/signup", data.model_dump())
        return resp

    async def _request(self, url, data:dict):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}/{url}/", json=data)
            return Result.model_construct(**response.json())
        except Exception as e:
            # raise
            return Result.resolve_exception(e)
