# indexer.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import json
import redis
from pymongo import MongoClient
from python_backend.config.settings import *
from python_backend.services.utils import make_doc_id



r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def tokenize(text):
    # very simple tokenizer; replace with better NLP for production
    return [t.lower() for t in text.split() if t.isalpha()]

def index():
    keys = r.keys("page:*")
    print("Found pages in Redis:", len(keys))
    for key in keys:
        raw = json.loads(r.get(key))
        if not raw:
            continue
        doc_id = raw["doc_id"]
        text = raw.get("text", "")
        title = raw.get("title", "")
        tokens = tokenize(title + " " + text)

        # store document metadata
        db.documents.update_one(
            {"doc_id": doc_id},
            {"$set": {"doc_id": doc_id, "url": raw["url"], "title": title, "length": len(tokens)}},
            upsert=True
        )

        counts = {}
        for t in tokens:
            counts[t] = counts.get(t, 0) + 1

        # update inverted index postings
        for term, tf in counts.items():
            db.inverted_index.update_one(
                {"term": term},
                {"$push": {"docs": {"doc_id": doc_id, "tf": tf}},
                 "$inc": {"df": 1}},
                upsert=True
            )

    print("Indexing complete")

if __name__ == "__main__":
    index()
