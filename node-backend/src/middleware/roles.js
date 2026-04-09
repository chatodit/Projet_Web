function requireRole(...roles) {
  return (req, res, next) => {
    if (!req.user || !roles.includes(req.user.role)) {
      return res.status(403).json({ error: true, message: 'Accès refusé — rôle insuffisant' });
    }
    next();
  };
}

module.exports = { requireRole };
