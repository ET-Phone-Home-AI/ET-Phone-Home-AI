import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

export default function Register() {
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  function update(field) {
    return e => setForm(f => ({ ...f, [field]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Registration failed');
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('role', data.role);
      localStorage.setItem('name', data.name);
      navigate('/chat');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <div style={styles.logo}>🦷</div>
        <h1 style={styles.title}>Create Patient Account</h1>
        <p style={styles.subtitle}>Orthodontic Patient Portal</p>

        {error && <div style={styles.error}>{error}</div>}

        <div style={styles.disclaimer}>
          ⚠️ This is an educational clinic portal. Please do not enter real personal health information.
        </div>

        <form onSubmit={handleSubmit} style={styles.form}>
          <label style={styles.label}>Full Name</label>
          <input value={form.name} onChange={update('name')} required style={styles.input} placeholder="Jane Smith" />
          <label style={styles.label}>Email</label>
          <input type="email" value={form.email} onChange={update('email')} required style={styles.input} placeholder="you@email.com" />
          <label style={styles.label}>Password</label>
          <input type="password" value={form.password} onChange={update('password')} required minLength={6} style={styles.input} placeholder="Min. 6 characters" />
          <button type="submit" style={styles.btn} disabled={loading}>
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <p style={styles.footer}>
          Already registered? <Link to="/login" style={styles.link}>Sign in</Link>
        </p>
      </div>
    </div>
  );
}

const styles = {
  page: { minHeight: '100vh', background: 'linear-gradient(135deg,#1a73e8 0%,#0d47a1 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 16 },
  card: { background: '#fff', borderRadius: 16, padding: '40px 36px', width: '100%', maxWidth: 420, boxShadow: '0 20px 60px rgba(0,0,0,0.15)' },
  logo: { fontSize: 48, textAlign: 'center', marginBottom: 8 },
  title: { textAlign: 'center', fontSize: 22, fontWeight: 700, color: '#1a1a2e', margin: '0 0 4px' },
  subtitle: { textAlign: 'center', color: '#666', margin: '0 0 16px', fontSize: 14 },
  disclaimer: { background: '#fff8e1', border: '1px solid #ffe082', borderRadius: 8, padding: '10px 14px', fontSize: 12, color: '#5d4037', marginBottom: 16 },
  error: { background: '#fde8e8', color: '#c62828', padding: '10px 14px', borderRadius: 8, marginBottom: 16, fontSize: 14 },
  form: { display: 'flex', flexDirection: 'column', gap: 4 },
  label: { fontSize: 13, fontWeight: 600, color: '#333', marginBottom: 4, marginTop: 8 },
  input: { padding: '10px 14px', borderRadius: 8, border: '1.5px solid #ddd', fontSize: 15, outline: 'none' },
  btn: { marginTop: 20, padding: '12px', borderRadius: 8, background: '#1a73e8', color: '#fff', fontSize: 15, fontWeight: 600, border: 'none', cursor: 'pointer' },
  footer: { textAlign: 'center', marginTop: 20, fontSize: 14, color: '#555' },
  link: { color: '#1a73e8', fontWeight: 600, textDecoration: 'none' },
};
