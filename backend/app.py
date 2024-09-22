from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import router
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
