from cleantext import clean
from copy import deepcopy
from pymongo import MongoClient
import os
import re
from bson.objectid import ObjectId
client = MongoClient(os.environ.get("MONGODB"))
db = client["doc_stock"]
docs = db["docs"]
def find_intersect(query, page_content):
    return list(set(query).intersection(page_content))
async def select_chunk(docs, query:str, k:int):
    query = clean(query, no_line_breaks=True, no_emoji=True)
    query = re.sub('[^0-9a-zA-Z]+', ' ', query)
    print(query)
    query = query.split(' ')
    exist_ids = []
    print(len(docs))
    for i, doc in enumerate(docs):
        page_content = clean(
            doc.page_content, no_line_breaks=True, no_emoji=True)
        page_content = re.sub('[^0-9a-zA-Z]+', ' ', page_content)
        page_content = page_content.split(' ')
        intersects = find_intersect(query, page_content)
        if len(intersects) == 0:
            continue
        exist_ids.append({
            'id': i,
            'n_intersect': len(intersects)
        })
    exist_ids = sorted(exist_ids, key = lambda x: x['n_intersect'], reverse=True)
    exist_ids = exist_ids[:k]
    exist_ids = sorted(exist_ids, key= lambda x: x['id'])
    ids = [x['id'] for x in exist_ids]
    print(ids)
    chunks = [docs[i] for i in ids]
    for i, doc in enumerate(docs):
        if len(chunks) >= k:
            break
        if i in ids:
            continue
        chunks.append(docs[i])
    return chunks

