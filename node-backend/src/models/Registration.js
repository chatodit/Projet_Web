const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Registration = sequelize.define('Registration', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true,
  },
  event_id: {
    type: DataTypes.INTEGER,
    allowNull: false,
  },
  participant_id: {
    type: DataTypes.INTEGER,
    allowNull: false,
  },
  registered_at: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW,
  },
}, {
  tableName: 'events_registration',
  timestamps: false,
  indexes: [
    {
      unique: true,
      fields: ['event_id', 'participant_id'],
    },
  ],
});

module.exports = Registration;
