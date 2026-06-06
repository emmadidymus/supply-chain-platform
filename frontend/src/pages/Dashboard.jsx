import { useEffect, useState } from 'react';
import { getSuppliers, getInventory, getSimulations } from '../api/endpoints';
import { Users, Package, Activity, AlertTriangle, TrendingUp, Shield } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';

const COLORS = ['#22c55e', '#f59e0b', '#ef4444'];

function StatCard({ icon: Icon, label, value, color, sub }) {
  return (
    <div style={{ background: '#fff', borderRadius: 12, padding: 24, boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
      borderLeft: `4px solid ${color}` }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <p style={{ margin: 0, fontSize: 13, color: '#64748b', fontWeight: 500 }}>{label}</p>
          <p style={{ margin: '8px 0 4px', fontSize: 28, fontWeight: 700, color: '#0f172a' }}>{value}</p>
          {sub && <p style={{ margin: 0, fontSize: 12, color: '#94a3b8' }}>{sub}</p>}
        </div>
        <div style={{ background: color + '20', padding: 12, borderRadius: 10 }}>
          <Icon size={22} color={color} />
        </div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [suppliers, setSuppliers] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [simulations, setSimulations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getSuppliers(), getInventory(), getSimulations()])
      .then(([s, inv, sim]) => {
        setSuppliers(s.data);
        setInventory(inv.data);
        setSimulations(sim.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const latestSim = simulations.find(s => s.status === 'completed');
  const baseline = latestSim?.results?.baseline;

  const criticalStock = inventory.filter(i => i.stockout_risk === 'critical').length;
  const highRiskSuppliers = suppliers.filter(s => s.risk_score > 0.4).length;

  const riskPieData = baseline ? [
    { name: 'On Time', value: Math.round(baseline.on_time_probability * 100) },
    { name: 'Shortage', value: Math.round(baseline.shortage_probability * 100) },
    { name: 'Severe', value: Math.round(baseline.severe_disruption_probability * 100) },
  ] : [];

  const supplierBarData = suppliers.slice(0, 8).map(s => ({
    name: s.name.length > 12 ? s.name.slice(0, 12) + '…' : s.name,
    risk: Math.round(s.risk_score * 100),
  }));

  const inventoryRiskData = [
    { label: 'Critical', count: inventory.filter(i => i.stockout_risk === 'critical').length, color: '#ef4444' },
    { label: 'High',     count: inventory.filter(i => i.stockout_risk === 'high').length,     color: '#f59e0b' },
    { label: 'Medium',   count: inventory.filter(i => i.stockout_risk === 'medium').length,   color: '#3b82f6' },
    { label: 'Low',      count: inventory.filter(i => i.stockout_risk === 'low').length,      color: '#22c55e' },
  ];

  if (loading) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60vh' }}>
      <div style={{ textAlign: 'center', color: '#64748b' }}>
        <Activity size={40} style={{ marginBottom: 12, opacity: 0.5 }} />
        <p>Loading dashboard…</p>
      </div>
    </div>
  );

  return (
    <div>
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ margin: 0, fontSize: 24, fontWeight: 700, color: '#0f172a' }}>Risk Dashboard</h1>
        <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: 14 }}>
          Supply chain health overview — {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
        </p>
      </div>

      {/* Stat Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 20, marginBottom: 28 }}>
        <StatCard icon={Users}         label="Total Suppliers"    value={suppliers.length}  color="#3b82f6" sub={`${highRiskSuppliers} high risk`} />
        <StatCard icon={Package}       label="Inventory Items"    value={inventory.length}  color="#8b5cf6" sub={`${criticalStock} critical`} />
        <StatCard icon={Activity}      label="Simulations Run"    value={simulations.length} color="#06b6d4" sub="Monte Carlo" />
        <StatCard icon={Shield}        label="Service Level"
          value={baseline ? `${Math.round(baseline.service_level * 100)}%` : '—'}
          color="#22c55e" sub={baseline ? 'Latest simulation' : 'No simulation yet'} />
      </div>

      {/* Alerts */}
      {(criticalStock > 0 || highRiskSuppliers > 0) && (
        <div style={{ background: '#fef2f2', border: '1px solid #fca5a5', borderRadius: 12, padding: '14px 20px',
          marginBottom: 28, display: 'flex', alignItems: 'center', gap: 12 }}>
          <AlertTriangle size={20} color="#dc2626" />
          <span style={{ fontSize: 14, color: '#dc2626', fontWeight: 500 }}>
            {criticalStock > 0 && `${criticalStock} item(s) at critical stock level. `}
            {highRiskSuppliers > 0 && `${highRiskSuppliers} high-risk supplier(s) detected.`}
          </span>
        </div>
      )}

      {/* Charts Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 20 }}>

        {/* Simulation Results Pie */}
        <div style={{ background: '#fff', borderRadius: 12, padding: 24, boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h3 style={{ margin: '0 0 20px', fontSize: 16, fontWeight: 600, color: '#0f172a' }}>
            Fulfillment Probability Distribution
          </h3>
          {riskPieData.length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={riskPieData} cx="50%" cy="50%" innerRadius={60} outerRadius={90}
                    dataKey="value" nameKey="name" label={({ name, value }) => `${value}%`}>
                    {riskPieData.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
                  </Pie>
                  <Tooltip formatter={(v) => `${v}%`} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginTop: 16 }}>
                {[
                  { label: 'On Time', value: `${Math.round(baseline.on_time_probability * 100)}%`, color: '#22c55e' },
                  { label: 'Shortage', value: `${Math.round(baseline.shortage_probability * 100)}%`, color: '#f59e0b' },
                  { label: 'Severe', value: `${Math.round(baseline.severe_disruption_probability * 100)}%`, color: '#ef4444' },
                ].map(({ label, value, color }) => (
                  <div key={label} style={{ textAlign: 'center', padding: '12px 8px', background: color + '10', borderRadius: 8 }}>
                    <div style={{ fontSize: 20, fontWeight: 700, color }}>{value}</div>
                    <div style={{ fontSize: 11, color: '#64748b', marginTop: 2 }}>{label}</div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div style={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: '#94a3b8', flexDirection: 'column', gap: 8 }}>
              <Activity size={36} style={{ opacity: 0.4 }} />
              <p style={{ margin: 0, fontSize: 14 }}>Run a simulation to see results</p>
            </div>
          )}
        </div>

        {/* Supplier Risk Bar Chart */}
        <div style={{ background: '#fff', borderRadius: 12, padding: 24, boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h3 style={{ margin: '0 0 20px', fontSize: 16, fontWeight: 600, color: '#0f172a' }}>Supplier Risk Scores</h3>
          {supplierBarData.length > 0 ? (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={supplierBarData} layout="vertical" margin={{ left: 10 }}>
                <XAxis type="number" domain={[0, 100]} tickFormatter={v => `${v}%`} fontSize={11} />
                <YAxis type="category" dataKey="name" width={90} fontSize={11} />
                <Tooltip formatter={v => [`${v}%`, 'Risk Score']} />
                <Bar dataKey="risk" radius={[0, 4, 4, 0]}>
                  {supplierBarData.map((entry, i) => (
                    <Cell key={i} fill={entry.risk > 40 ? '#ef4444' : entry.risk > 20 ? '#f59e0b' : '#22c55e'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ height: 260, display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: '#94a3b8', flexDirection: 'column', gap: 8 }}>
              <Users size={36} style={{ opacity: 0.4 }} />
              <p style={{ margin: 0, fontSize: 14 }}>Add suppliers to see risk scores</p>
            </div>
          )}
        </div>
      </div>

      {/* Inventory Risk Summary */}
      <div style={{ background: '#fff', borderRadius: 12, padding: 24, boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <h3 style={{ margin: '0 0 16px', fontSize: 16, fontWeight: 600, color: '#0f172a' }}>Inventory Health Summary</h3>
        <div style={{ display: 'flex', gap: 16 }}>
          {inventoryRiskData.map(({ label, count, color }) => (
            <div key={label} style={{ flex: 1, padding: 20, background: color + '10',
              borderRadius: 10, border: `1px solid ${color}30`, textAlign: 'center' }}>
              <div style={{ fontSize: 32, fontWeight: 700, color }}>{count}</div>
              <div style={{ fontSize: 13, color: '#64748b', marginTop: 4 }}>{label} Risk</div>
            </div>
          ))}
        </div>
        {baseline && (
          <div style={{ marginTop: 20, padding: '14px 20px', background: '#f8fafc', borderRadius: 8,
            display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
            {[
              { label: 'Risk Exposure Score', value: `${baseline.risk_exposure_score}/100` },
              { label: 'Expected Shortage Cost', value: `$${baseline.expected_shortage_cost_usd?.toLocaleString()}` },
              { label: 'Avg Shortage Units', value: baseline.avg_shortage_units_per_run },
              { label: 'Iterations Run', value: baseline.num_iterations?.toLocaleString() },
            ].map(({ label, value }) => (
              <div key={label} style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 18, fontWeight: 700, color: '#0f172a' }}>{value}</div>
                <div style={{ fontSize: 12, color: '#64748b' }}>{label}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
