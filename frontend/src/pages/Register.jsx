import React, { useState } from 'react';
import api from '../api/axios';
import { useNavigate, Link } from 'react-router-dom';

const Register = () => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        first_name: '',
        last_name: ''
    });
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            // On envoie les données à l'URL d'inscription
            await api.post('auth/register/', formData);
            alert("Compte créé avec succès ! Vous pouvez maintenant vous connecter.");
            navigate('/'); // On redirige vers le Login
        } catch (err) {
            console.error(err);
            alert("Erreur lors de l'inscription. L'utilisateur existe peut-être déjà.");
        }
    };

    return (
        <div style={s.container}>
            <div style={s.card}>
                <div style={s.header}>
                    <h1 style={s.logo}>EventHub</h1>
                    <p style={s.subtitle}>Créez votre compte pour gérer vos événements</p>
                </div>

                <form onSubmit={handleSubmit} style={s.form}>
                    <div style={s.row}>
                        <input 
                            style={s.input} 
                            type="text" 
                            placeholder="Prénom" 
                            onChange={e => setFormData({...formData, first_name: e.target.value})} 
                            required 
                        />
                        <input 
                            style={s.input} 
                            type="text" 
                            placeholder="Nom" 
                            onChange={e => setFormData({...formData, last_name: e.target.value})} 
                            required 
                        />
                    </div>
                    <input 
                        style={s.input} 
                        type="text" 
                        placeholder="Nom d'utilisateur" 
                        onChange={e => setFormData({...formData, username: e.target.value})} 
                        required 
                    />
                    <input 
                        style={s.input} 
                        type="email" 
                        placeholder="Email" 
                        onChange={e => setFormData({...formData, email: e.target.value})} 
                        required 
                    />
                    <input 
                        style={s.input} 
                        type="password" 
                        placeholder="Mot de passe" 
                        onChange={e => setFormData({...formData, password: e.target.value})} 
                        required 
                    />
                    
                    <button type="submit" style={s.btn}>S'inscrire</button>
                </form>

                <p style={s.footerText}>
                    Déjà un compte ? <Link to="/" style={s.link}>Se connecter</Link>
                </p>
            </div>
        </div>
    );
};

const s = {
    container: { backgroundColor: '#f4f7f6', height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', fontFamily: 'Segoe UI, sans-serif' },
    card: { backgroundColor: '#fff', padding: '40px', borderRadius: '12px', boxShadow: '0 10px 25px rgba(0,0,0,0.1)', width: '100%', maxWidth: '450px' },
    header: { textAlign: 'center', marginBottom: '30px' },
    logo: { margin: 0, color: '#2d3436', fontSize: '26px', fontWeight: 'bold' },
    subtitle: { color: '#636e72', fontSize: '14px', marginTop: '5px' },
    form: { display: 'flex', flexDirection: 'column', gap: '15px' },
    row: { display: 'flex', gap: '10px' },
    input: { padding: '12px', borderRadius: '6px', border: '1px solid #dfe6e9', fontSize: '15px', flex: 1 },
    btn: { backgroundColor: '#00b894', color: '#fff', border: 'none', padding: '12px', borderRadius: '6px', fontSize: '16px', fontWeight: 'bold', cursor: 'pointer', marginTop: '10px' },
    footerText: { textAlign: 'center', marginTop: '20px', fontSize: '14px', color: '#636e72' },
    link: { color: '#0984e3', textDecoration: 'none', fontWeight: 'bold' }
};

export default Register;