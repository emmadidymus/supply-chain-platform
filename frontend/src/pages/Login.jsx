import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../api/endpoints';
import { TrendingUp } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('admin@supplychain.com');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true); setError('');
    try {
      const res = await login(email, password);
      localStorage.setItem('token', res.data.access_token);
      navigate('/');
    } catch {
      setError('Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'system-ui, sans-serif' }}>
      <div style={{ background: '#fff', borderRadius: 16, padding: 40, width: 380, boxShadow: '0 25px 50px rgba(0,0,0,0.3)' }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
            <TrendingUp size={28} color="#3b82f6" />
            <span style={{ fontSize: 20, fontWeight: 700, color: '#0f172a' }}>Supply Chain Risk</span>
          </div>
          <p style={{ color: '#64748b', fontSize: 14, margin: 0 }}>Sign in to your platform</p>
        </div>

        <form onSubmit={handleLogin}>
          {[
            { label: 'Email', value: email, set: setEmail, type: 'email' },
            { label: 'Password', value: password, set: setPassword, type: 'password' },
          ].map(({ label, value, set, type }) => (
            <div key={label} style={{ marginBottom: 16 }}>
              <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: '#374151', marginBottom: 6 }}>{label}</label>
              <input type={type} value={value} onChange={e => set(e.target.value)} required
                style={{ width: '100%', padding: '10px 14px', border: '1px solid #d1d5db', borderRadius: 8,
                  fontSize: 14, outline: 'none', boxSizing: 'border-box' }} />
            </div>
          ))}

          {error && <div style={{ background: '#fef2f2', border: '1px solid #fca5a5', color: '#dc2626',
            padding: '10px 14px', borderRadius: 8, fontSize: 13, marginBottom: 16 }}>{error}</div>}

          <button type="submit" disabled={loading}
            style={{ width: '100%', padding: '12px', background: '#2563eb', color: '#fff',
              border: 'none', borderRadius: 8, fontSize: 15, fontWeight: 600, cursor: 'pointer',
              opacity: loading ? 0.7 : 1 }}>
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
}
