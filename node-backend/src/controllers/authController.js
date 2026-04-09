const jwt = require('jsonwebtoken');
const { User } = require('../models');

async function register(req, res, next) {
  try {
    const { username, email, password, role } = req.body;
    if (!username || !email || !password) {
      return res.status(400).json({ error: true, message: 'username, email et password sont requis' });
    }
    const existing = await User.findOne({ where: { email } });
    if (existing) {
      return res.status(400).json({ error: true, message: 'Cet email est déjà utilisé' });
    }
    const user = await User.create({ username, email, password, role });
    return res.status(201).json({
      id: user.id,
      username: user.username,
      email: user.email,
      role: user.role,
    });
  } catch (err) {
    next(err);
  }
}

async function login(req, res, next) {
  try {
    const { username, password } = req.body;
    if (!username || !password) {
      return res.status(400).json({ error: true, message: 'username et password sont requis' });
    }
    const user = await User.findOne({ where: { username } });
    if (!user || !user.checkPassword(password)) {
      return res.status(401).json({ error: true, message: 'Identifiants invalides' });
    }
    const token = jwt.sign(
      { id: user.id, username: user.username, role: user.role },
      process.env.JWT_SECRET,
      { expiresIn: '1h' }
    );
    return res.json({ access: token, user: { id: user.id, username: user.username, role: user.role } });
  } catch (err) {
    next(err);
  }
}

async function me(req, res, next) {
  try {
    const user = await User.findByPk(req.user.id, {
      attributes: ['id', 'username', 'email', 'role', 'date_joined'],
    });
    if (!user) return res.status(404).json({ error: true, message: 'Utilisateur introuvable' });
    return res.json({
      id: user.id,
      username: user.username,
      email: user.email,
      role: user.role,
      date_joined: user.date_joined,
    });
  } catch (err) {
    next(err);
  }
}

async function changePassword(req, res, next) {
  try {
    const { old_password, new_password } = req.body;
    if (!old_password || !new_password) {
      return res.status(400).json({ error: true, message: 'old_password et new_password sont requis' });
    }
    const user = await User.findByPk(req.user.id);
    if (!user || !user.checkPassword(old_password)) {
      return res.status(400).json({ old_password: ['Mot de passe actuel incorrect.'] });
    }
    if (new_password.length < 8) {
      return res.status(400).json({ new_password: ['Le mot de passe doit contenir au moins 8 caractères.'] });
    }
    // Utilise le hook beforeCreate pour hacher — on doit appeler manuellement
    const crypto = require('crypto');
    const iterations = 870000;
    const salt = crypto.randomBytes(9).toString('base64').slice(0, 12);
    const hash = crypto.pbkdf2Sync(new_password, salt, iterations, 32, 'sha256').toString('base64');
    user.password = `pbkdf2_sha256$${iterations}$${salt}$${hash}`;
    await user.save();
    return res.json({ detail: 'Mot de passe modifié avec succès.' });
  } catch (err) {
    next(err);
  }
}

module.exports = { register, login, me, changePassword };
