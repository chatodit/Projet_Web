import React, { useEffect, useState } from 'react';
import api from '../api/axios';

const Dashboard = () => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [newEvent, setNewEvent] = useState({ title: '', description: '', location: '', date: '' });

    const fetchEvents = async () => {
        try {
            const res = await api.get('events/');
            setEvents(res.data.results || res.data);
        } catch (err) { console.error(err); }
        finally { setLoading(false); }
    };

    useEffect(() => { fetchEvents(); }, []);

    const handleCreate = async (e) => {
        e.preventDefault();
        try {
            await api.post('events/', newEvent);
            setNewEvent({ title: '', description: '', location: '', date: '' });
            fetchEvents();
        } catch (err) { alert("Erreur lors de la création."); }
    };

    const handleDelete = async (id) => {
        if (window.confirm("Supprimer cet événement ?")) {
            try {
                await api.delete(`events/${id}/`);
                fetchEvents();
            } catch (err) { alert("Action non autorisée."); }
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        window.location.href = "/";
    };

    if (loading) return <div style={s.loader}>Chargement...</div>;

    return (
        <div style={s.container}>
            {/* HEADER */}
            <header style={s.header}>
                <h1 style={s.logo}> EventHub <span style={s.badge}></span></h1>
                <button onClick={logout} style={s.logoutBtn}>Déconnexion</button>
            </header>

            <div style={s.content}>
                {/* FORMULAIRE (Sidebar gauche) */}
                <aside style={s.sidebar}>
                    <div style={s.card}>
                        <h3 style={s.cardTitle}>Nouvel Événement</h3>
                        <form onSubmit={handleCreate} style={s.form}>
                            <input style={s.input} type="text" placeholder="Titre" value={newEvent.title} onChange={e => setNewEvent({...newEvent, title: e.target.value})} required />
                            <textarea style={s.textarea} placeholder="Description" value={newEvent.description} onChange={e => setNewEvent({...newEvent, description: e.target.value})} required />
                            <input style={s.input} type="text" placeholder="Lieu" value={newEvent.location} onChange={e => setNewEvent({...newEvent, location: e.target.value})} required />
                            <input style={s.input} type="datetime-local" value={newEvent.date} onChange={e => setNewEvent({...newEvent, date: e.target.value})} required />
                            <button type="submit" style={s.submitBtn}>Créer</button>
                        </form>
                    </div>
                </aside>

                {/* LISTE (Grille droite) */}
                <main style={s.main}>
                    <h2 style={s.sectionTitle}>Événements à venir ({events.length})</h2>
                    <div style={s.grid}>
                        {events.map(event => (
                            <div key={event.id} style={s.eventCard}>
                                <div style={s.eventBody}>
                                    <h4 style={s.eventTitle}>{event.title}</h4>
                                    <p style={s.eventDesc}>{event.description}</p>
                                    <div style={s.eventMeta}>
                                        <span>📍 {event.location}</span>
                                        <span>⏰ {new Date(event.date).toLocaleDateString()}</span>
                                    </div>
                                </div>
                                <button onClick={() => handleDelete(event.id)} style={s.deleteBtn}>🗑️</button>
                            </div>
                        ))}
                    </div>
                </main>
            </div>
        </div>
    );
};

// --- STYLES (CSS-in-JS) ---
const s = {
    container: { backgroundColor: '#f4f7f6', minHeight: '100vh', fontFamily: 'Segoe UI, sans-serif' },
    header: { backgroundColor: '#fff', padding: '15px 40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 2px 10px rgba(0,0,0,0.05)' },
    logo: { margin: 0, fontSize: '24px', color: '#2d3436' },
    badge: { fontSize: '12px', backgroundColor: '#e17055', color: '#fff', padding: '3px 8px', borderRadius: '10px', verticalAlign: 'middle' },
    logoutBtn: { backgroundColor: '#636e72', color: '#fff', border: 'none', padding: '8px 15px', borderRadius: '5px', cursor: 'pointer' },
    content: { display: 'flex', padding: '30px', gap: '30px', maxWidth: '1200px', margin: '0 auto' },
    sidebar: { flex: '1' },
    main: { flex: '3' },
    card: { backgroundColor: '#fff', padding: '20px', borderRadius: '10px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' },
    cardTitle: { marginTop: 0, color: '#2d3436', borderBottom: '2px solid #0984e3', paddingBottom: '10px' },
    form: { display: 'flex', flexDirection: 'column', gap: '10px' },
    input: { padding: '10px', borderRadius: '5px', border: '1px solid #dfe6e9' },
    textarea: { padding: '10px', borderRadius: '5px', border: '1px solid #dfe6e9', minHeight: '80px' },
    submitBtn: { backgroundColor: '#00b894', color: '#fff', border: 'none', padding: '12px', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold' },
    sectionTitle: { marginTop: 0, color: '#2d3436' },
    grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px' },
    eventCard: { backgroundColor: '#fff', borderRadius: '10px', overflow: 'hidden', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', boxShadow: '0 4px 6px rgba(0,0,0,0.05)', position: 'relative', border: '1px solid #eee' },
    eventBody: { padding: '20px' },
    eventTitle: { margin: '0 0 10px 0', color: '#0984e3', fontSize: '18px' },
    eventDesc: { color: '#636e72', fontSize: '14px', marginBottom: '15px' },
    eventMeta: { display: 'flex', flexDirection: 'column', gap: '5px', fontSize: '12px', color: '#b2bec3' },
    deleteBtn: { position: 'absolute', top: '10px', right: '10px', background: 'none', border: 'none', cursor: 'pointer', fontSize: '18px', opacity: '0.6' },
    loader: { display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontSize: '20px', color: '#636e72' }
};

export default Dashboard;