const express = require('express');
const router = express.Router();

router.get('/', (req, res) => {
  res.json({ message: 'Users API endpoints - coming soon!', version: '0.1.0-mvp' });
});

module.exports = router;
