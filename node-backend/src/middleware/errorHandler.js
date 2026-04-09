const { UniqueConstraintError, ValidationError } = require('sequelize');

function errorHandler(err, req, res, next) {
  if (err instanceof UniqueConstraintError) {
    return res.status(409).json({
      error: true,
      status: 409,
      message: 'Conflit — cette ressource existe déjà',
      details: err.errors.map((e) => e.message),
    });
  }
  if (err instanceof ValidationError) {
    return res.status(400).json({
      error: true,
      status: 400,
      message: 'Données invalides',
      details: err.errors.map((e) => e.message),
    });
  }
  const status = err.status || 500;
  return res.status(status).json({
    error: true,
    status,
    message: err.message || 'Erreur interne du serveur',
    details: {},
  });
}

module.exports = errorHandler;
