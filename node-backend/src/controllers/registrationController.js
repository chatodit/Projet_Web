const { Registration, Event, Participant } = require('../models');

async function list(req, res, next) {
  try {
    const registrations = await Registration.findAll({
      include: [
        { model: Event, attributes: ['id', 'title', 'date', 'status'] },
        { model: Participant, attributes: ['id', 'first_name', 'last_name', 'email'] },
      ],
      order: [['registered_at', 'DESC']],
    });
    return res.json(registrations);
  } catch (err) {
    next(err);
  }
}

async function create(req, res, next) {
  try {
    const { eventId, event_id, participantId, participant_id } = req.body;
    const eid = event_id || eventId;
    const pid = participant_id || participantId;
    if (!eid || !pid) {
      return res.status(400).json({ error: true, message: 'event_id et participant_id sont requis' });
    }
    const event = await Event.findByPk(eid);
    if (!event) return res.status(404).json({ error: true, message: 'Événement introuvable' });
    if (event.status === 'cancelled') {
      return res.status(400).json({ error: true, message: "Impossible de s'inscrire à un événement annulé" });
    }
    const existing = await Registration.findOne({ where: { event_id: eid, participant_id: pid } });
    if (existing) {
      return res.status(409).json({ error: true, message: 'Ce participant est déjà inscrit à cet événement' });
    }
    const reg = await Registration.create({ event_id: eid, participant_id: pid });
    return res.status(201).json(reg);
  } catch (err) {
    next(err);
  }
}

async function getOne(req, res, next) {
  try {
    const reg = await Registration.findByPk(req.params.id, {
      include: [
        { model: Event, attributes: ['id', 'title', 'date', 'status'] },
        { model: Participant, attributes: ['id', 'first_name', 'last_name', 'email'] },
      ],
    });
    if (!reg) return res.status(404).json({ error: true, message: 'Inscription introuvable' });
    return res.json(reg);
  } catch (err) {
    next(err);
  }
}

async function remove(req, res, next) {
  try {
    const reg = await Registration.findByPk(req.params.id);
    if (!reg) return res.status(404).json({ error: true, message: 'Inscription introuvable' });
    await reg.destroy();
    return res.status(204).send();
  } catch (err) {
    next(err);
  }
}

module.exports = { list, create, getOne, remove };
