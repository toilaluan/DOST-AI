from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import openai
from services import store_embeddings
from model import DostChat
import os
from dotenv import load_dotenv
import asyncio
load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")


class MyApp(FastAPI):
    def __init__(self):
        super().__init__()
        self.baseDoc = None
        self.routes()

    def routes(self):
        @self.post("/init")
        async def init(data: dict):
            id = data.get("id")
            self.baseDoc = DostChat(id)
            return "ready"

        @self.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            response = asyncio.wait_for(self.baseDoc.init_query(), timeout=50)
            init_mes = await response
            await websocket.send_text(init_mes)
            while True:
                data = await websocket.receive_text()
                response = asyncio.wait_for(self.baseDoc.doc_query(str(data)), timeout=50)
                reply = await response
                await websocket.send_text(reply)

        @self.post("/upload_init_embed")
        async def init_embed(data: dict):
            id = data.get("id")
            await store_embeddings(id)
            return "updated embeds"


app = MyApp()
