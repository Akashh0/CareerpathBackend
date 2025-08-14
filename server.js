// server.js
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');
const axios = require('axios');

const app = express();
app.use(cors());
app.use(bodyParser.json());

// ✅ Serve roadmap PDFs from roadmaps folder
const roadmapsPath = path.join(__dirname, 'roadmaps');
app.use('/roadmaps', express.static(roadmapsPath)); // fixed route

// ✅ Proxy route to Python backend (Flask)
app.post('/api/generate-roadmap', async (req, res) => {
  try {
    const flaskRes = await axios.post(
      'http://localhost:5000/api/generate-roadmap',
      req.body,
      { headers: { 'Content-Type': 'application/json' } }
    );
    res.json(flaskRes.data);
  } catch (err) {
    console.error('❌ Proxy error:', err.message);
    res.status(500).json({ error: 'Failed to fetch roadmap from Python backend.' });
  }
});

// ✅ Health check
app.get('/', (req, res) => {
  res.send('Express backend running ✅');
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`🚀 Express server running on port ${PORT}`);
  console.log(`📄 Serving PDFs from: ${roadmapsPath}`);
});
