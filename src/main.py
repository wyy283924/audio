from fastapi import FastAPI
from api.v1.routers import routers

app = FastAPI()
app.include_router(routers)