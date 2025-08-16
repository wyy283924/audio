from fastapi import FastAPI
from src.api.v1.routers import routers

app = FastAPI()
app.include_router(routers)