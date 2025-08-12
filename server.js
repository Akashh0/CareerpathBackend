const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');
const roadmapRoute = require('./routes/roadmap');

const app = express();
app.use(cors());
app.use(bodyParser.json());

// ✅ Allow external CSS (e.g., antd) + local media
app.use((req, res, next) => {
  res.setHeader(
    "Content-Security-Policy",
    "default-src 'self'; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; font-src 'self' https://cdn.jsdelivr.net;"
  );
  next();
});

// ✅ Shared roadmaps folder at project root
const roadmapsPath = path.join(__dirname, '..', 'roadmaps');
app.use('/media', express.static(roadmapsPath));

// Routes
app.use('/api', roadmapRoute);

const PORT = 3000;
app.listen(PORT, () => {
  console.log(` Express server running on port ${PORT}`);
  console.log(` Serving PDFs from: ${roadmapsPath}`);
});
