from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from web.api import modlogs, settings
from web.auth import require_token
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="HyperGriot Dashboard")

app.include_router(modlogs.router)
app.include_router(settings.router)

app.mount("/", StaticFiles(directory="web/static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web.main:app", host="127.0.0.1", port=int(os.getenv("WEB_PORT", 8000)), reload=True)
