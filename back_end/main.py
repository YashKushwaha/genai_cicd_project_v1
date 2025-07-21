from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import os
import asyncio

from pathlib import Path

from back_end.config_settings import STATIC_DIR, IMAGES_DIR
from back_end.routes import ui_routes, debug_routes, api_routes

app = FastAPI()

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

app.include_router(ui_routes.router)
app.include_router(debug_routes.router)
app.include_router(api_routes.router)

if __name__ == "__main__":
    import uvicorn
    app_path = Path(__file__).resolve().with_suffix('').name  # gets filename without .py
    uvicorn.run(f"{app_path}:app", host="localhost", port=8000, reload=True, workers = 4)