from utils import *
class ChatDoc:
    def __init__(self, link):
        link = link.split('/')
        self.id = link[link.index('d')+1]
        self.doc = read_pdf(self.id)
        self.doc_embeds = doc_to_embeddings(self.doc)
        print(self.doc_embeds)
    def doc_query(self, q):
        return query(self.doc_embeds, q)