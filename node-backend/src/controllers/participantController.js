const { Participant, Registration, Event } = require('../models');

async function list(req, res, next) {
  try {
    const participants = await Participant.findAll({ order: [['last_name', 'ASC']] });
    return res.json(participants);
  } catch (err) {
    next(err);
  }
}

async function create(req, res, next) {
  try {
    const { firstName, first_name, lastName, last_name, email, phone } = req.body;
    const fn = first_name || firstName;
    const ln = last_name || lastName;
    if (!fn || !ln || !email) {
      return res.status(400).json({ error: true, message: 'first_name, last_name et email sont requis' });
    }
    const participant = await Participant.create({ first_name: fn, last_name: ln, email, phone });
    return res.status(201).json(participant);
  } catch (err) {
    next(err);
  }
}

async function getOne(req, res, next) {
  try {
    const participant = await Participant.findByPk(req.params.id, {
      include: [{
        model: Registration,
        include: [{ model: Event, attributes: ['id', 'title', 'date', 'status'] }],
      }],
    });
    if (!participant) return res.status(404).json({ error: true, message: 'Participant introuvable' });
    return res.json(participant);
  } catch (err) {
    next(err);
  }
}

async function update(req, res, next) {
  try {
    const participant = await Participant.findByPk(req.params.id);
    if (!participant) return res.status(404).json({ error: true, message: 'Participant introuvable' });
    const { firstName, first_name, lastName, last_name, email, phone } = req.body;
    await participant.update({
      first_name: first_name || firstName || participant.first_name,
      last_name: last_name || lastName || participant.last_name,
      email: email || participant.email,
      phone: phone || participant.phone,
    });
    return res.json(participant);
  } catch (err) {
    next(err);
  }
}

async function remove(req, res, next) {
  try {
    const participant = await Participant.findByPk(req.params.id);
    if (!participant) return res.status(404).json({ error: true, message: 'Participant introuvable' });
    await participant.destroy();
    return res.status(204).send();
  } catch (err) {
    next(err);
  }
}

module.exports = { list, create, getOne, update, remove };
