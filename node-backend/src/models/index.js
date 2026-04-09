const sequelize = require('../config/database');
const User = require('./User');
const Event = require('./Event');
const Participant = require('./Participant');
const Registration = require('./Registration');

Event.belongsTo(User, { foreignKey: 'created_by_id', as: 'creator' });
User.hasMany(Event, { foreignKey: 'created_by_id' });

Registration.belongsTo(Event, { foreignKey: 'event_id' });
Registration.belongsTo(Participant, { foreignKey: 'participant_id' });
Event.hasMany(Registration, { foreignKey: 'event_id' });
Participant.hasMany(Registration, { foreignKey: 'participant_id' });

module.exports = { sequelize, User, Event, Participant, Registration };
