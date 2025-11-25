# pagerank.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pymongo import MongoClient
from python_backend.config.settings import *


db = MongoClient(MONGO_URI)[DB_NAME]

DAMPING = 0.85
ITERATIONS = 20

def compute():
    docs = list(db.documents.find({}))
    N = len(docs)
    if N == 0:
        print("No docs found in DB.")
        return

    # initialize
    for doc in docs:
        db.documents.update_one({"doc_id": doc["doc_id"]}, {"$set": {"pagerank": 1.0 / N}})

    for it in range(ITERATIONS):
        print("PageRank iteration", it+1)
        new_scores = {}
        for doc in docs:
            doc_id = doc["doc_id"]
            incoming_entry = db.backlinks.find_one({"doc_id": doc_id}) or {}
            incoming = incoming_entry.get("incoming", [])
            score_sum = 0.0
            for src in incoming:
                src_doc = db.documents.find_one({"doc_id": src})
                if not src_doc:
                    continue
                src_pr = src_doc.get("pagerank", 0.0)
                src_out = db.backlinks.find_one({"doc_id": src}) or {}
                out_count = src_out.get("outgoing_count", 0) or 1
                score_sum += src_pr / out_count
            new_score = (1 - DAMPING) / N + DAMPING * score_sum
            new_scores[doc_id] = new_score

        # write back
        for doc_id, val in new_scores.items():
            db.documents.update_one({"doc_id": doc_id}, {"$set": {"pagerank": val}})

    print("PageRank computed")

if __name__ == "__main__":
    compute()
