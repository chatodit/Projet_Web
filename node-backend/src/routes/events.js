const router = require('express').Router();
const { list, create, getOne, update, remove, register, unregister } = require('../controllers/eventController');
const { authenticate } = require('../middleware/auth');
const { requireRole } = require('../middleware/roles');

router.get('/', authenticate, list);
router.post('/', authenticate, requireRole('admin', 'editor'), create);
router.get('/:id', authenticate, getOne);
router.put('/:id', authenticate, requireRole('admin', 'editor'), update);
router.delete('/:id', authenticate, requireRole('admin'), remove);
router.post('/:id/register', authenticate, requireRole('viewer'), register);
router.delete('/:id/unregister', authenticate, requireRole('viewer'), unregister);

module.exports = router;
