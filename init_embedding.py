import numpy as np
import openai
import pandas as pd
from pymongo import MongoClient
from bson.objectid import ObjectId
from utils import doc_to_embeddings, read_pdf
client = MongoClient('mongodb://localhost:27017/')
EMBEDDING_MODEL = "text-embedding-ada-002"
CHAT_MODEL = "gpt-3.5-turbo"
API_KEY = "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"
openai.api_key = API_KEY

def store_embeddings(id: str):
    db = client['doc_stock']
    docs = db['docs']
    doc_id = ObjectId(id)
    doc = docs.find_one({'_id': doc_id})
    
    link = doc['link'].split('/')
    drive_id = link[link.index('d')+1]
    doc = read_pdf(drive_id)
    
    doc_embeds = doc_to_embeddings(doc)
    update = {'$set': {'embed': doc_embeds} }
    filter = {'_id': doc_id}
    result = docs.update_one(filter, update)
    

    



