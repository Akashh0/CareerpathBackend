const express = require('express');
const cors = require('cors');
const app = express();

const roadmapRoute = require('./routes/roadmap'); // 👈 Import route

app.use(cors());
app.use(express.json());

// Use the route
app.use('/api', roadmapRoute); // Your frontend will call: /api/generate-roadmap

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
