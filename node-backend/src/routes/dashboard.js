const router = require('express').Router();
const { getDashboard } = require('../controllers/dashboardController');
const { authenticate } = require('../middleware/auth');
const { requireRole } = require('../middleware/roles');

router.get('/', authenticate, requireRole('admin', 'editor'), getDashboard);

module.exports = router;
