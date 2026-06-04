import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const form = new URLSearchParams();
      form.append('username', email);
      form.append('password', password);
      const res = await fetch('/api/auth/login', { method: 'POST', body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Login failed');
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('role', data.role);
      localStorage.setItem('name', data.name);
      navigate(data.role === 'professor' ? '/dashboard' : '/chat');
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
        <h1 style={styles.title}>Orthodontic Patient Portal</h1>
        <p style={styles.subtitle}>Sign in to your account</p>

        {error && <div style={styles.error}>{error}</div>}

        <form onSubmit={handleSubmit} style={styles.form}>
          <label style={styles.label}>Email</label>
          <input
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            required
            style={styles.input}
            placeholder="you@email.com"
          />
          <label style={styles.label}>Password</label>
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            required
            style={styles.input}
            placeholder="••••••••"
          />
          <button type="submit" style={styles.btn} disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p style={styles.footer}>
          New patient? <Link to="/register" style={styles.link}>Create account</Link>
        </p>
        <p style={styles.hint}>Professor login: professor@clinic.edu / professor123</p>
      </div>
    </div>
  );
}

const styles = {
  page: { minHeight: '100vh', background: 'linear-gradient(135deg,#1a73e8 0%,#0d47a1 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 16 },
  card: { background: '#fff', borderRadius: 16, padding: '40px 36px', width: '100%', maxWidth: 420, boxShadow: '0 20px 60px rgba(0,0,0,0.15)' },
  logo: { fontSize: 48, textAlign: 'center', marginBottom: 8 },
  title: { textAlign: 'center', fontSize: 22, fontWeight: 700, color: '#1a1a2e', margin: '0 0 4px' },
  subtitle: { textAlign: 'center', color: '#666', margin: '0 0 24px', fontSize: 14 },
  error: { background: '#fde8e8', color: '#c62828', padding: '10px 14px', borderRadius: 8, marginBottom: 16, fontSize: 14 },
  form: { display: 'flex', flexDirection: 'column', gap: 4 },
  label: { fontSize: 13, fontWeight: 600, color: '#333', marginBottom: 4, marginTop: 8 },
  input: { padding: '10px 14px', borderRadius: 8, border: '1.5px solid #ddd', fontSize: 15, outline: 'none', transition: 'border 0.2s' },
  btn: { marginTop: 20, padding: '12px', borderRadius: 8, background: '#1a73e8', color: '#fff', fontSize: 15, fontWeight: 600, border: 'none', cursor: 'pointer' },
  footer: { textAlign: 'center', marginTop: 20, fontSize: 14, color: '#555' },
  link: { color: '#1a73e8', fontWeight: 600, textDecoration: 'none' },
  hint: { textAlign: 'center', fontSize: 11, color: '#aaa', marginTop: 12 },
};
