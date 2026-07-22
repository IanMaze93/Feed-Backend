from fastapi import FastAPI

from src.handlers.health import health_handler
from src.handlers.root import root_handler

app = FastAPI(
    title="Feed Backend API",
    version="0.1.0",
    description="Core API gateway for Feed services.",
)


@app.get("/health")
def health():
    return health_handler()


@app.get("/")
def root():
    return root_handler()
