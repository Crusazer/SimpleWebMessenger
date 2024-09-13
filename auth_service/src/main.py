from fastapi import FastAPI

from .api.auth import router as auth_router
from .api.users import router as user_router
from .logger_configs.logging_config import setup_logging

#setup_logging()
app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)
