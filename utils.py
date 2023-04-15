import numpy as np
import openai
import pandas as pd
import pickle
import fitz
import tiktoken
import gdown
EMBEDDING_MODEL = "text-embedding-ada-002"
CHAT_MODEL = "gpt-3.5-turbo"
API_KEY = "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"
openai.api_key = API_KEY
def get_embedding(text: str, model: str=EMBEDDING_MODEL) -> list[float]:
    result = openai.Embedding.create(
      model=model,
      input=text,
    )
    return result["data"][0]["embedding"]
def doc_to_embeddings(doc) -> dict:
    de = {
        'text': [],
        'embed': []
    }
    doc = partition_doc(doc)
    for part in doc:
        e = get_embedding(part)
        de['text'].append(part)
        de['embed'].append(e)
    return pd.DataFrame(de)
def vector_similarity(x: list[float], y: list[float]) -> float:
    """
    Returns the similarity between two vectors.
    
    Because OpenAI Embeddings are normalized to length 1, the cosine similarity is the same as the dot product.
    """
    return np.dot(np.array(x), np.array(y))

def order_document_sections_by_query_similarity(query: str, contexts: dict[str, np.array]) -> list[(float, (str, str))]:
    """
    Find the query embedding for the supplied query, and compare it against all of the pre-calculated document embeddings
    to find the most relevant sections. 
    
    Return the list of document sections, sorted by relevance in descending order.
    """
    query_embedding = get_embedding(query)
    
    document_similarities = sorted([
        (vector_similarity(query_embedding, doc_embedding), doc_index) for doc_index, doc_embedding in contexts.items()
    ], reverse=True)
    return document_similarities
def query(de: pd.DataFrame, q: str):
    e_q = get_embedding(q)
    de['dist'] = [vector_similarity(e_q, e) for e in de['embed']]
    de.sort_values(by=['dist'], ascending=False)
    selected_part = de.iloc[0]
    text = selected_part['text']
    prompts = f'''We have provided context information below: \n"
            "---------------------\n"
            "{text}\n"
            "---------------------\n"
            "Given this information, Please answer my question in the same language that I used to ask you.\n"
            "Please answer the question: {q}\n'''
    reply = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "user", "content": prompts},
        ]
    )
    return reply['choices'][0]['message']['content']
def read_pdf(id: str) -> list[str]:
    path = gdown.download(id=id, output='cached/cached_file.pdf')
    doc = fitz.open(path)
    return doc
def partition_doc(doc, max_tokens = 3500):
    enc = tiktoken.encoding_for_model("gpt-4")
    tokens_per_page = []

    for page in doc:
        tokens = enc.encode(page.get_text())
        tokens_per_page.append(len(tokens))
    
    minidocs = []
    current_tokens = 0
    current_doc = ''
    for page, n_tokens in zip(doc, tokens_per_page):
        if current_tokens + n_tokens <= max_tokens:
            current_doc += ' ' + page.get_text()
            current_tokens += n_tokens
        else:
            minidocs.append(current_doc)
            current_doc = page.get_text()
            current_tokens = n_tokens
    minidocs.append(current_doc)
    return minidocs