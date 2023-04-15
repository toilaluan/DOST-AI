from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import openai
from ChatDoc import ChatDoc

openai.api_key = "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"


class MyApp(FastAPI):
    def __init__(self):
        super().__init__()
        self.baseDoc = None
        self.routes()

    def routes(self):
        @self.post("/init")
        async def init(data: dict):
            link = data.get("link")
            self.baseDoc = ChatDoc(link)
            return {"received_message": link}

        @self.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            init_mes = self.baseDoc.doc_query('Act as a document assistance, generate some question for this article and make reader feel interesting')
            await websocket.send_text(init_mes)
            while True:
                data = await websocket.receive_text()
                reply = self.baseDoc.doc_query(data)
                await websocket.send_text(reply)


app = MyApp()
