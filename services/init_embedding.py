from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import TokenTextSplitter
from langchain.document_loaders import UnstructuredPDFLoader
import gdown
import os
from pymongo import MongoClient
from bson.objectid import ObjectId
import chromadb
import torch
from dotenv import load_dotenv
load_dotenv()
client = MongoClient(os.environ.get("MONGODB"))
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL")
CHAT_MODEL = os.environ.get("CHAT_MODEL")
CHROMA_ROOT = os.environ.get("CHROMA_ROOT")


def download_pdf(id: str):
    db = client["doc_stock"]
    docs = db["docs"]
    doc_id = ObjectId(id)
    doc = docs.find_one({"_id": doc_id})
    link = doc["link"].split("/")
    drive_id = link[link.index("d") + 1]
    path = gdown.download(id=drive_id, output="cached_file.pdf")
    return path


def id_to_texts(id: str, chunk_size: int):
    path = download_pdf(id)
    loader = UnstructuredPDFLoader(path)
    data = loader.load()
    text_splitter = TokenTextSplitter(
        chunk_size=chunk_size, chunk_overlap=0)
    texts = text_splitter.split_documents(data)
    return texts


async def store_embeddings(id: str, chunk_size: int = 1000):
    texts = id_to_texts(id, chunk_size)
    persist_directory = os.path.join(CHROMA_ROOT, id)
    embeddings = HuggingFaceEmbeddings()
    client_settings = chromadb.config.Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=persist_directory,
        anonymized_telemetry=False,
    )
    vectorstore = Chroma(
        collection_name=id,
        embedding_function=embeddings,
        client_settings=client_settings,
        persist_directory=persist_directory,
    )
    vectorstore.add_documents(
        texts
    )
    vectorstore.persist()
    print("Init successfully!")
    torch.cuda.empty_cache()
