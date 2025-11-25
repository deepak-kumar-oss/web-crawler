import subprocess
import sys
import time
import os

# Helper: run a python file and print nice logs
def run_step(name, cmd):
    print(f"\n==============================")
    print(f" 🚀 Running: {name}")
    print(f"==============================\n")

    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ ERROR running: {name}")
        sys.exit(1)
    else:
        print(f"✅ Completed: {name}\n")
        time.sleep(1)  # small pause for safety


if __name__ == "__main__":
    print("======================================")
    print(" 📌 Starting FULL Search Engine Pipeline")
    print("======================================\n")

    # IMPORTANT: use python_backend/<file>.py, not services/<file>.py
    run_step("Spider (Crawler)", "python3 python_backend/services/spider.py")
    run_step("Indexer", "python3 python_backend/services/indexer.py")
    run_step("Backlinks Processor", "python3 python_backend/services/backlinks.py")
    run_step("PageRank", "python3 python_backend/services/pagerank.py")
    run_step("TF-IDF", "python3 python_backend/services/tfidf.py")

    print("\n======================================")
    print(" 🎉 All tasks completed successfully!")
    print(" Database is fully updated.")
    print("======================================\n")
