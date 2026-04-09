const { Op, fn, col, literal } = require('sequelize');
const { Event, Participant, Registration, sequelize } = require('../models');

async function getDashboard(req, res, next) {
  try {
    const [totalEvents, totalParticipants, totalRegistrations, eventsByStatusRaw, upcomingEvents] =
      await Promise.all([
        Event.count(),
        Participant.count(),
        Registration.count(),
        Event.findAll({
          attributes: ['status', [fn('COUNT', col('id')), 'total']],
          group: ['status'],
          raw: true,
        }),
        Event.findAll({
          where: { date: { [Op.gte]: new Date() }, status: { [Op.ne]: 'cancelled' } },
          order: [['date', 'ASC']],
          limit: 5,
          attributes: ['id', 'title', 'date', 'location', 'status'],
        }),
      ]);

    const events_by_status = { planned: 0, ongoing: 0, completed: 0, cancelled: 0 };
    for (const row of eventsByStatusRaw) {
      events_by_status[row.status] = parseInt(row.total || 0, 10);
    }

    return res.json({
      total_events: totalEvents,
      events_by_status,
      total_participants: totalParticipants,
      total_registrations: totalRegistrations,
      upcoming_events: upcomingEvents,
    });
  } catch (err) {
    next(err);
  }
}

module.exports = { getDashboard };
