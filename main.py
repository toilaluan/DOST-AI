from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import openai
from ChatDoc import ChatDoc
from init_embedding import store_embeddings
openai.api_key = "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"


class MyApp(FastAPI):
    def __init__(self):
        super().__init__()
        self.baseDoc = None
        self.routes()

    def routes(self):
        @self.post("/init")
        async def init(data: dict):
            id = data.get("id")
            self.baseDoc = ChatDoc(id)
            return "ready for chat"

        @self.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            init_mes = self.baseDoc.doc_query('introduce you as a assistant, who help for query about this document')
            print(init_mes)
            await websocket.send_text(init_mes)
            while True:
                data = await websocket.receive_text()
                reply = self.baseDoc.doc_query(data)
                await websocket.send_text(reply)
        @self.post("/upload_init_embed")
        async def init_embed(data: dict):
            id = data.get("id")
            store_embeddings(id)
            return "updated embeds"

app = MyApp()
