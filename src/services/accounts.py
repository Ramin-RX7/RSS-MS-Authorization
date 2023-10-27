import httpx

from config import SETTINGS
from schemas import Signup,Login



class AccountsService:
    def __init__(self, base_url=None, api_key=None):
        self.base_url = base_url or SETTINGS.ACCOUNTS_SERVICE_BASE_URL
        self.api_key = api_key or SETTINGS.ACCOUNTS_SERVICE_API_KEY

    async def login(self, data:Login):
        resp = await self._request("login", data)
        return resp

    async def signup(self, data:Signup):
        resp = await self._request("signup", data)
        return resp

    async def _request(self, url, data:dict):
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/{url}", data=data)
            return response
