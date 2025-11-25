// server.js
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { MongoClient } = require('mongodb');

const PORT = process.env.PORT || 3000;
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017';
const DB_NAME = process.env.DB_NAME || 'search_engine';
const PR_WEIGHT = parseFloat(process.env.SCORE_WEIGHT_PR || '0.3');
const TF_WEIGHT = parseFloat(process.env.SCORE_WEIGHT_TFIDF || '0.7');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static('client'));

let db, invertedCol, docsCol;

async function initMongo() {
  const client = new MongoClient(MONGO_URI);
  await client.connect();
  db = client.db(DB_NAME);
  invertedCol = db.collection('inverted_index');
  docsCol = db.collection('documents');
  console.log('Connected to MongoDB');
}

function tokenize(q) {
  if (!q) return [];
  return q.split(/\s+/).map(t => t.toLowerCase()).filter(t => /^[a-z]+$/.test(t));
}

app.get('/api/search', async (req, res) => {
  const q = req.query.q || '';
  const terms = tokenize(q);
  if (terms.length === 0) return res.json([]);

  try {
    // gather candidate scores (in-memory)
    const candidateScores = {}; // doc_id -> tfidf score sum
    for (const term of terms) {
      const entry = await invertedCol.findOne({ term: term });
      if (!entry) continue;
      const idf = entry.idf || 0;
      const docs = entry.docs || [];
      for (const p of docs) {
        const docId = p.doc_id;
        const tf = p.tf || 1;
        const tfWeight = tf > 0 ? (1 + Math.log(tf)) : 0;
        const score = tfWeight * idf;
        candidateScores[docId] = (candidateScores[docId] || 0) + score;
      }
    }

    // fetch doc meta for candidates and combine with pagerank
    const docIds = Object.keys(candidateScores);
    const docsCursor = await docsCol.find({ doc_id: { $in: docIds } }).toArray();
    const results = docsCursor.map(d => {
      const tfidfScore = candidateScores[d.doc_id] || 0;
      const pr = d.pagerank || 0;
      const final = TF_WEIGHT * tfidfScore + PR_WEIGHT * pr;
      return { title: d.title || d.url, url: d.url, score: final, doc_id: d.doc_id };
    });

    results.sort((a, b) => b.score - a.score);
    res.json(results.slice(0, 50));
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'server error' });
  }
});

app.get('/', (req, res) => {
  res.sendFile(__dirname + '/client/index.html');
});

initMongo().then(() => {
  app.listen(PORT, () => {
    console.log(`Server listening on http://localhost:${PORT}`);
  });
}).catch(err => {
  console.error('Failed to init', err);
  process.exit(1);
});
