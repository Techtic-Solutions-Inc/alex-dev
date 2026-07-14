from fastapi import FastAPI
from src.middlewares.error_handling import error_handling_middleware

app = FastAPI()
app.add_middleware(error_handling_middleware)
