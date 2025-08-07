// roadmap.js ✅ FIXED
const express = require('express');
const axios = require('axios');
const router = express.Router();

router.post('/generate-roadmap', async (req, res) => {
  const { interest, qualification } = req.body;

  try {
    // ✅ Corrected endpoint
    const response = await axios.post('http://localhost:5000/api/generate-roadmap', {
  interest,
  qualification,
});

    res.json(response.data);
  } catch (error) {
  console.error('Error generating roadmap:', error.message);
  if (error.response) {
    console.error('Flask Response:', error.response.data);  // ✅ Add this
  }
  res.status(500).json({ error: 'Failed to generate roadmap' });
}

});

module.exports = router;
