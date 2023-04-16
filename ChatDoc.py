from utils import *
from pymongo import MongoClient
from bson.objectid import ObjectId
client = MongoClient('mongodb://localhost:27017/')
import pandas as pd
class ChatDoc:
    def __init__(self, id):
        db = client['doc_stock']
        docs = db['docs']
        doc_id = ObjectId(id)
        doc = docs.find_one({'_id': doc_id})
        self.doc_embeds = pd.DataFrame(doc['embed'])
    def doc_query(self, q):
        return query(self.doc_embeds, q)