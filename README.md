# 🔍 Mini Search Engine (Python + Node.js)

A fully working mini search engine built from scratch using:

- **Python Crawler (Async Spider)**
- **Redis (Crawl storage)**
- **MongoDB (Index storage)**
- **PageRank**
- **TF-IDF**
- **Node.js Search API**
- **Frontend Web Client**

This project mimics how early Google worked using a crawl → index → rank pipeline.

---

## 🚀 Features

### 🕸 1. Async Web Crawler (Spider)
- Fast async crawler using **aiohttp**
- Normalizes URLs
- Restricts crawling to one domain
- Extracts:
  - Title
  - Text
  - Outlinks
  - Images
- Stores raw page data in **Redis**

### 📑 2. Indexer
- Reads crawled pages from Redis
- Cleans text
- Creates inverted index
- Saves structured documents to **MongoDB**

### 🔗 3. Backlinks Processor
- Reads outlinks from each document
- Creates backlink graph
- Stores in MongoDB

### ⭐ 4. PageRank
- Runs iterative PageRank (Google 1999 algorithm)
- Calculates importance score of each page

### 📊 5. TF-IDF Weighting
- Computes keyword importance for each document
- Used to rank search results

### 💻 6. Node.js Search API
- Simple REST API to search documents
- Combines TF-IDF + PageRank for ranking
- Returns title, URL and snippet

### 🌐 7. Frontend Search UI
- Basic web interface (HTML/JS)
- Calls backend API for results

---

# 🛠️ Project Structure


---

# ⚙️ Installation & Setup

## 1️⃣ Install Dependencies

### 🔸 Inside WSL (Ubuntu)
Install system requirements:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv redis-server
sudo apt install -y mongodb-org    # if not installed


cd python_backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


sudo service redis-server start
sudo service mongod start


backend:
cd ~/search-engine-hybrid
source python_backend/venv/bin/activate
python3 -m python_backend.pipeline


frontend:
cd node-frontend
npm install
node server.js
# web-crawler
