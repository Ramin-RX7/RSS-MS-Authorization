from fastapi import FastAPI

from config import SETTINGS

from api import router




app = FastAPI()

app.include_router(router)

@app.get("/")
async def index():
    return {}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("__main__:app", host="0.0.0.0", port=8001, reload=True)
