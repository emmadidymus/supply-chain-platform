import { useEffect, useState } from 'react';
import { getSuppliers, createSupplier, deleteSupplier } from '../api/endpoints';
import { Plus, Trash2, AlertTriangle, CheckCircle, Shield } from 'lucide-react';

function RiskBadge({ score }) {
  const pct = Math.round(score * 100);
  const color = pct > 40 ? '#ef4444' : pct > 20 ? '#f59e0b' : '#22c55e';
  const label = pct > 40 ? 'High' : pct > 20 ? 'Medium' : 'Low';
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, padding: '3px 10px',
      borderRadius: 20, background: color + '15', color, fontSize: 12, fontWeight: 600 }}>
      {pct > 40 ? <AlertTriangle size={11} /> : <CheckCircle size={11} />}
      {label} ({pct}%)
    </span>
  );
}

export default function Suppliers() {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', location: '', reliability_score: 0.8,
    lead_time_days: 14, failure_probability: 0.05, contact_email: '' });

  const load = () => getSuppliers().then(r => setSuppliers(r.data)).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    await createSupplier({ ...form, reliability_score: +form.reliability_score,
      lead_time_days: +form.lead_time_days, failure_probability: +form.failure_probability });
    setShowForm(false);
    setForm({ name: '', location: '', reliability_score: 0.8, lead_time_days: 14, failure_probability: 0.05, contact_email: '' });
    load();
  };

  const handleDelete = async (id) => {
    if (window.confirm('Delete this supplier?')) { await deleteSupplier(id); load(); }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 24, fontWeight: 700, color: '#0f172a' }}>Suppliers</h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: 14 }}>Manage and monitor supplier risk</p>
        </div>
        <button onClick={() => setShowForm(!showForm)}
          style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 18px',
            background: '#2563eb', color: '#fff', border: 'none', borderRadius: 8,
            fontSize: 14, fontWeight: 600, cursor: 'pointer' }}>
          <Plus size={16} /> Add Supplier
        </button>
      </div>

      {/* Add Form */}
      {showForm && (
        <div style={{ background: '#fff', borderRadius: 12, padding: 24, marginBottom: 24,
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)', border: '1px solid #e2e8f0' }}>
          <h3 style={{ margin: '0 0 20px', fontSize: 16, fontWeight: 600 }}>New Supplier</h3>
          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
              {[
                { label: 'Name *', key: 'name', type: 'text' },
                { label: 'Location *', key: 'location', type: 'text' },
                { label: 'Contact Email', key: 'contact_email', type: 'email' },
                { label: 'Reliability Score (0-1)', key: 'reliability_score', type: 'number', step: '0.01', min: 0, max: 1 },
                { label: 'Lead Time (days)', key: 'lead_time_days', type: 'number', min: 1 },
                { label: 'Failure Probability (0-1)', key: 'failure_probability', type: 'number', step: '0.01', min: 0, max: 1 },
              ].map(({ label, key, ...props }) => (
                <div key={key}>
                  <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#374151', marginBottom: 6 }}>{label}</label>
                  <input {...props} value={form[key]} onChange={e => setForm({ ...form, [key]: e.target.value })}
                    style={{ width: '100%', padding: '9px 12px', border: '1px solid #d1d5db',
                      borderRadius: 7, fontSize: 13, boxSizing: 'border-box' }} />
                </div>
              ))}
            </div>
            <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>
              <button type="submit" style={{ padding: '9px 20px', background: '#2563eb', color: '#fff',
                border: 'none', borderRadius: 7, fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>
                Save Supplier
              </button>
              <button type="button" onClick={() => setShowForm(false)}
                style={{ padding: '9px 20px', background: '#f1f5f9', color: '#475569',
                  border: 'none', borderRadius: 7, fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Table */}
      <div style={{ background: '#fff', borderRadius: 12, boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
        {loading ? (
          <div style={{ padding: 40, textAlign: 'center', color: '#94a3b8' }}>Loading suppliers…</div>
        ) : suppliers.length === 0 ? (
          <div style={{ padding: 60, textAlign: 'center', color: '#94a3b8' }}>
            <Shield size={40} style={{ opacity: 0.3, marginBottom: 12 }} />
            <p style={{ margin: 0 }}>No suppliers yet. Add your first supplier above.</p>
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                {['Name', 'Location', 'Reliability', 'Lead Time', 'Fail Prob.', 'Risk Score', ''].map(h => (
                  <th key={h} style={{ padding: '12px 16px', textAlign: 'left', fontSize: 12,
                    fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {suppliers.map((s, i) => (
                <tr key={s.id} style={{ borderBottom: '1px solid #f1f5f9',
                  background: i % 2 === 0 ? '#fff' : '#fafafa' }}>
                  <td style={{ padding: '14px 16px', fontWeight: 600, color: '#0f172a', fontSize: 14 }}>{s.name}</td>
                  <td style={{ padding: '14px 16px', color: '#64748b', fontSize: 13 }}>{s.location}</td>
                  <td style={{ padding: '14px 16px', color: '#0f172a', fontSize: 13 }}>{(s.reliability_score * 100).toFixed(0)}%</td>
                  <td style={{ padding: '14px 16px', color: '#0f172a', fontSize: 13 }}>{s.lead_time_days}d</td>
                  <td style={{ padding: '14px 16px', color: '#0f172a', fontSize: 13 }}>{(s.failure_probability * 100).toFixed(1)}%</td>
                  <td style={{ padding: '14px 16px' }}><RiskBadge score={s.risk_score} /></td>
                  <td style={{ padding: '14px 16px' }}>
                    <button onClick={() => handleDelete(s.id)}
                      style={{ padding: '6px 8px', background: '#fef2f2', border: 'none',
                        borderRadius: 6, cursor: 'pointer', color: '#dc2626' }}>
                      <Trash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
