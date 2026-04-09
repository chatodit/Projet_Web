const { DataTypes } = require('sequelize');
const crypto = require('crypto');
const sequelize = require('../config/database');

const User = sequelize.define('User', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true,
  },
  username: {
    type: DataTypes.STRING(150),
    allowNull: false,
    unique: true,
  },
  email: {
    type: DataTypes.STRING(254),
    allowNull: false,
  },
  password: {
    type: DataTypes.STRING(128),
    allowNull: false,
  },
  role: {
    type: DataTypes.STRING(10),
    defaultValue: 'viewer',
  },
  first_name: {
    type: DataTypes.STRING(150),
    defaultValue: '',
  },
  last_name: {
    type: DataTypes.STRING(150),
    defaultValue: '',
  },
  is_active: {
    type: DataTypes.BOOLEAN,
    defaultValue: true,
  },
  is_staff: {
    type: DataTypes.BOOLEAN,
    defaultValue: false,
  },
  is_superuser: {
    type: DataTypes.BOOLEAN,
    defaultValue: false,
  },
  last_login: {
    type: DataTypes.DATE,
    allowNull: true,
  },
  date_joined: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW,
  },
}, {
  tableName: 'accounts_user',
  timestamps: false,
});

// Hash PBKDF2 compatible Django
User.beforeCreate(async (user) => {
  user.password = hashPassword(user.password);
});

function hashPassword(plain) {
  const iterations = 870000;
  const salt = crypto.randomBytes(9).toString('base64').slice(0, 12);
  const hash = crypto.pbkdf2Sync(plain, salt, iterations, 32, 'sha256').toString('base64');
  return `pbkdf2_sha256$${iterations}$${salt}$${hash}`;
}

User.prototype.checkPassword = function (plain) {
  const encoded = this.password;
  // Format Django : pbkdf2_sha256$iterations$salt$hash
  if (encoded.startsWith('pbkdf2_sha256$')) {
    const parts = encoded.split('$');
    const iterations = parseInt(parts[1], 10);
    const salt = parts[2];
    const storedHash = parts[3];
    const derived = crypto.pbkdf2Sync(plain, salt, iterations, 32, 'sha256').toString('base64');
    return derived === storedHash;
  }
  return false;
};

module.exports = User;
