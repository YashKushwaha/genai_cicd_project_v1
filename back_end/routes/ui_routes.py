from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
import json
from back_end.config_settings import templates
from pathlib import Path
from fastapi.responses import FileResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "chat_endpoint": "/echo"
    })

@router.get("/chat", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "chat_endpoint": "/chat"
    })

@router.get("/echo", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "chat_endpoint": "/echo"
    })


