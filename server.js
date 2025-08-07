const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');
const roadmapRoute = require('./routes/roadmap');

const app = express();
app.use(cors());
app.use(bodyParser.json());

// ✅ Add this line to serve PDFs
app.use('/media', express.static(path.join(__dirname, 'roadmaps')));

// Use your roadmap route
app.use('/api', roadmapRoute);

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`🚀 Express server running on port ${PORT}`);
});
