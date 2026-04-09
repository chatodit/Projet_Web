# EventHub — Backend Node.js/Express

API REST développée avec Node.js, Express et Sequelize (SQLite), répliquant les fonctionnalités du backend Django EventHub.

## Prérequis

- Node.js >= 18
- npm >= 9

## Installation et lancement

```bash
cd node-backend
npm install
npm run dev      # développement (nodemon)
npm start        # production
```

Le serveur démarre sur `http://localhost:3000`.

---

## Connexion avec le frontend

Le fichier à modifier est `frontend/src/api/axios.js`, ligne `baseURL`.

**Connecter au backend Node.js (ce projet) :**
```js
baseURL: 'http://localhost:3000/api/',
```

**Connecter au backend Django :**
```js
baseURL: 'http://127.0.0.1:8000/api/',
```

C'est le seul changement nécessaire.

---

## Endpoints

### Authentification

| Méthode | Route | Description | Auth |
|---------|-------|-------------|------|
| POST | `/api/auth/register` | Créer un compte | Non |
| POST | `/api/auth/login` | Se connecter (retourne un JWT) | Non |
| GET | `/api/auth/me` | Infos de l'utilisateur connecté | Oui |

**Exemple login :**
```json
POST /api/auth/login
{ "username": "alice", "password": "secret123" }

Réponse : { "access": "<jwt>", "user": { "id": 1, "username": "alice", "role": "admin" } }
```

---

### Événements

| Méthode | Route | Description | Rôles |
|---------|-------|-------------|-------|
| GET | `/api/events/` | Liste des événements (filtres: search, status, date_from, date_to) | tous |
| POST | `/api/events/` | Créer un événement | admin, editor |
| GET | `/api/events/:id` | Détail d'un événement + participants | tous |
| PUT | `/api/events/:id` | Modifier un événement | admin, editor |
| DELETE | `/api/events/:id` | Supprimer un événement | admin |
| POST | `/api/events/:id/register` | S'inscrire à un événement | viewer |
| DELETE | `/api/events/:id/unregister` | Se désinscrire d'un événement | viewer |

---

### Participants

| Méthode | Route | Description | Rôles |
|---------|-------|-------------|-------|
| GET | `/api/participants/` | Liste des participants | admin, editor |
| POST | `/api/participants/` | Créer un participant | admin, editor |
| GET | `/api/participants/:id` | Détail + événements inscrits | admin, editor |
| PUT | `/api/participants/:id` | Modifier un participant | admin, editor |
| DELETE | `/api/participants/:id` | Supprimer un participant | admin |

---

### Inscriptions

| Méthode | Route | Description | Rôles |
|---------|-------|-------------|-------|
| GET | `/api/registrations/` | Liste des inscriptions | admin, editor |
| POST | `/api/registrations/` | Créer une inscription | admin, editor |
| GET | `/api/registrations/:id` | Détail d'une inscription | admin, editor |
| DELETE | `/api/registrations/:id` | Supprimer une inscription | admin |

---

### Dashboard

| Méthode | Route | Description | Rôles |
|---------|-------|-------------|-------|
| GET | `/api/dashboard/` | Statistiques globales | admin, editor |

**Réponse :**
```json
{
  "total_events": 10,
  "events_by_status": { "planned": 4, "ongoing": 2, "completed": 3, "cancelled": 1 },
  "total_participants": 45,
  "total_registrations": 78,
  "upcoming_events": [...]
}
```

---

## Authentification

Toutes les routes protégées nécessitent un header :
```
Authorization: Bearer <token>
```

Les rôles disponibles sont : `admin`, `editor`, `viewer`.

---

## Analyse comparative — Django + DRF vs Node.js + Express

### Tableau comparatif

| Critère | Django + DRF | Node.js + Express |
|---------|-------------|-------------------|
| **Philosophie** | "Batteries included" — tout intégré | Minimaliste — composition libre |
| **ORM** | Django ORM (migrations auto, admin) | Sequelize (manuel, flexible) |
| **Auth JWT** | `djangorestframework-simplejwt` | `jsonwebtoken` (custom) |
| **Validation** | Serializers déclaratifs | Manuelle dans les controllers |
| **Permissions** | Classes de permission réutilisables | Middleware personnalisé |
| **Documentation API** | `drf-spectacular` → Swagger auto | Manuel (ou Swagger JSDoc) |
| **Performance** | Synchrone, moins adapté aux I/O | Asynchrone natif (event loop) |
| **Courbe d'apprentissage** | Forte au départ, très productif ensuite | Faible au départ, complexité croissante |
| **Cas d'usage idéal** | Applications CRUD complexes, admin, équipes | APIs légères, microservices, temps réel |

### Points forts de Django + DRF

- **Moins de boilerplate** : les serializers valident, sérialisent et documentent en même temps. En Express, chaque opération est écrite manuellement.
- **ORM puissant** : les migrations sont générées automatiquement à partir des modèles. Avec Sequelize, `sync()` convient au développement mais n'est pas adapté à la production (pas de migration versionnée).
- **Interface d'administration** : Django Admin offre gratuitement une interface CRUD complète, sans une ligne de code frontend.
- **Permissions déclaratives** : `IsAuthenticated`, `IsAdminUser` sont des classes réutilisables et testables. En Express, chaque middleware de rôle est écrit à la main.
- **Sécurité par défaut** : protection CSRF, validation stricte des types, serializers qui empêchent la suraffectation de masse.

### Points forts de Node.js + Express

- **Performances I/O** : le modèle asynchrone non-bloquant gère mieux les connexions simultanées nombreuses (WebSockets, streaming, SSE).
- **Même langage front/back** : partage de types, de validateurs et de logique métier entre frontend React et backend — réduit le coût de context-switching.
- **Écosystème npm** : plus de 2 millions de packages disponibles ; intégration facile avec des services tiers modernes.
- **Flexibilité architecturale** : aucune convention imposée, adapté aux microservices, aux fonctions serverless et aux architectures événementielles.
- **Temps réel natif** : intégration naturelle avec Socket.io pour des fonctionnalités de chat, notifications ou collaboration en direct.

### Conclusion

Pour une application comme EventHub — orientée CRUD, avec des rôles, une administration et des équipes de développeurs — **Django + DRF est le choix le plus productif** : moins de code à écrire, plus de fonctionnalités "gratuites", et une meilleure maintenabilité à long terme.

Node.js + Express devient pertinent si EventHub évolue vers des fonctionnalités temps réel (notifications live, tableau de bord en push), ou s'il est déployé comme un microservice léger dans une infrastructure plus large.
