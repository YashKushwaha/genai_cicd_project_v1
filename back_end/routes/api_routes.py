from fastapi import Form, File, UploadFile
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi import APIRouter, Request
import asyncio

router = APIRouter()

async def stream_llm_response(llm, prompt: str):
    response = llm.stream_complete(prompt)
    for chunk in response:
        yield chunk.delta
        await asyncio.sleep(0.1)

async def stream_response(response):
    for chunk in response:
        yield chunk.delta
        await asyncio.sleep(0.1)

@router.post("/chat")
async def chat(request: Request, message: str = Form(...), image: UploadFile = File(None)):
    response_stream = stream_llm_response(request.app.state.llm, message)
    return StreamingResponse(response_stream, media_type="text/plain")

@router.post("/chat_bot")
async def chat_bot(request: Request, message: str = Form(...), image: UploadFile = File(None)):
    response_stream = stream_llm_response(request.app.state.chat_engine, message)
    return StreamingResponse(response_stream, media_type="text/plain")