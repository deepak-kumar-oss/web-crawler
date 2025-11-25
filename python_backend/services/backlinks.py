# backlinks.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import json, hashlib
import redis
from pymongo import MongoClient
from python_backend.config.settings import *
from python_backend.services.utils import make_doc_id


r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
db = MongoClient(MONGO_URI)[DB_NAME]

def run():
    keys = r.keys("page:*")
    for key in keys:
        raw = json.loads(r.get(key))
        if not raw:
            continue
        src_doc = raw["doc_id"]
        outlinks = raw.get("outlinks", [])
        # record outgoing count for src
        db.backlinks.update_one({"doc_id": src_doc}, {"$set": {"outgoing_count": len(outlinks)}}, upsert=True)
        for link in outlinks:
            link_id = hashlib.sha1(link.encode()).hexdigest()
            db.backlinks.update_one(
                {"doc_id": link_id},
                {"$addToSet": {"incoming": src_doc}},
                upsert=True
            )
    print("Backlinks processing complete")

if __name__ == "__main__":
    run()
