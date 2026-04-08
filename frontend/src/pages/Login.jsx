import React, { useState } from 'react';
import api from '../api/axios';
import { useNavigate, Link } from 'react-router-dom';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await api.post('auth/login/', { username, password });
            localStorage.setItem('token', res.data.access);
            navigate('/dashboard');
        } catch (err) {
            alert("Identifiants incorrects");
        }
    };

    return (
        <div style={s.container}>
            <div style={s.loginCard}>
                <div style={s.header}>
                    <h1 style={s.logo}>EventHub</h1>
                    <p style={s.subtitle}>Connectez-vous pour gérer vos événements</p>
                </div>

                <form onSubmit={handleSubmit} style={s.form}>
                    <div style={s.inputGroup}>
                        <label style={s.label}>Nom d'utilisateur</label>
                        <input 
                            style={s.input} 
                            type="text" 
                            placeholder="ex: admin" 
                            onChange={e => setUsername(e.target.value)} 
                            required 
                        />
                    </div>

                    <div style={s.inputGroup}>
                        <label style={s.label}>Mot de passe</label>
                        <input 
                            style={s.input} 
                            type="password" 
                            placeholder="••••••••" 
                            onChange={e => setPassword(e.target.value)} 
                            required 
                        />
                    </div>

                    <button type="submit" style={s.loginBtn}>Se connecter</button>
                </form>
                <p style={s.footerText}>
                    Pas encore de compte ? <Link to="/register" style={s.link}>Inscrivez-vous ici</Link>
                </p>

                <div style={s.footer}>
                    <p></p>
                </div>
            </div>
        </div>
    );
};

// --- STYLES ---
const s = {
    container: {
        backgroundColor: '#f4f7f6',
        height: '100vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif',
    },
    loginCard: {
        backgroundColor: '#fff',
        padding: '40px',
        borderRadius: '12px',
        boxShadow: '0 10px 25px rgba(0,0,0,0.1)',
        width: '100%',
        maxWidth: '400px',
    },
    header: {
        textAlign: 'center',
        marginBottom: '30px',
    },
    logo: {
        margin: 0,
        color: '#2d3436',
        fontSize: '28px',
        fontWeight: 'bold',
    },
    subtitle: {
        color: '#636e72',
        fontSize: '14px',
        marginTop: '5px',
    },
    form: {
        display: 'flex',
        flexDirection: 'column',
        gap: '20px',
    },
    inputGroup: {
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
    },
    label: {
        fontSize: '13px',
        fontWeight: '600',
        color: '#2d3436',
    },
    input: {
        padding: '12px',
        borderRadius: '6px',
        border: '1px solid #dfe6e9',
        fontSize: '15px',
        outlineColor: '#0984e3',
    },
    loginBtn: {
        backgroundColor: '#0984e3',
        color: '#fff',
        border: 'none',
        padding: '12px',
        borderRadius: '6px',
        fontSize: '16px',
        fontWeight: 'bold',
        cursor: 'pointer',
        transition: 'background 0.3s',
        marginTop: '10px',
    },
    footer: {
        marginTop: '30px',
        textAlign: 'center',
        borderTop: '1px solid #eee',
        paddingTop: '20px',
        fontSize: '12px',
        color: '#b2bec3',
    }
};

export default Login;