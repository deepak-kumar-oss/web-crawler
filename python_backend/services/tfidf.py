# tfidf.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import math
from pymongo import MongoClient
from python_backend.config.settings import *


db = MongoClient(MONGO_URI)[DB_NAME]

def compute():
    N = db.documents.count_documents({})
    if N == 0:
        print("No documents in DB.")
        return
    for term_doc in db.inverted_index.find({}):
        df = term_doc.get("df", 0)
        idf = math.log((N / (1 + df))) if df > 0 else 0.0
        db.inverted_index.update_one({"term": term_doc["term"]}, {"$set": {"idf": idf}})
    print("TF-IDF (IDF) computed")

if __name__ == "__main__":
    compute()
