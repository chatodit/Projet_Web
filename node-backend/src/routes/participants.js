const router = require('express').Router();
const { list, create, getOne, update, remove } = require('../controllers/participantController');
const { authenticate } = require('../middleware/auth');
const { requireRole } = require('../middleware/roles');

router.get('/', authenticate, requireRole('admin', 'editor'), list);
router.post('/', authenticate, requireRole('admin', 'editor'), create);
router.get('/:id', authenticate, requireRole('admin', 'editor'), getOne);
router.put('/:id', authenticate, requireRole('admin', 'editor'), update);
router.delete('/:id', authenticate, requireRole('admin'), remove);

module.exports = router;
