from fastapi import FastAPI

from config import SETTINGS

from api import router




app = FastAPI()

app.include_router(router)

@app.get("/")
async def index():
    return {}
