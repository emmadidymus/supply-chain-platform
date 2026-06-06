import { useEffect, useState, useRef } from 'react';
import { runSimulation, getSimulations, getSimulation } from '../api/endpoints';
import { Play, Clock, CheckCircle, XCircle, ChevronDown, ChevronUp, Zap } from 'lucide-react';

const statusIcon = { pending: <Clock size={14} />, running: <Clock size={14} />,
  completed: <CheckCircle size={14} />, failed: <XCircle size={14} /> };
const statusColor = { pending: '#f59e0b', running: '#3b82f6', completed: '#22c55e', failed: '#ef4444' };

const defaultScenarios = [
  { name: 'Supplier Failure', description: 'Primary supplier offline for 30 days',
    parameters: { type: 'supplier_failure', supplier_id: 1, duration_days: 30 } },
  { name: '40% Demand Surge', description: 'Holiday season demand spike',
    parameters: { type: 'demand_surge', multiplier: 1.4 } },
  { name: 'Shipping Delays +50%', description: 'Port congestion scenario',
    parameters: { type: 'shipping_delay', delay_multiplier: 1.5 } },
];

export default function Simulations() {
  const [simulations, setSimulations] = useState([]);
  const [expanded, setExpanded] = useState(null);
  const [running, setRunning] = useState(false);
  const [simName, setSimName] = useState('Risk Analysis ' + new Date().toLocaleDateString());
  const [iterations, setIterations] = useState(10000);
  const pollingRef = useRef(null);

  const load = () => getSimulations().then(r => setSimulations(r.data));
  useEffect(() => { load(); return () => clearInterval(pollingRef.current); }, []);

  const pollSimulation = (id) => {
    pollingRef.current = setInterval(async () => {
      const res = await getSimulation(id);
      if (res.data.status === 'completed' || res.data.status === 'failed') {
        clearInterval(pollingRef.current);
        setRunning(false);
        load();
      }
    }, 1500);
  };

  const handleRun = async () => {
    setRunning(true);
    try {
      const res = await runSimulation({ name: simName, num_iterations: +iterations, scenarios: defaultScenarios });
      load();
      pollSimulation(res.data.id);
    } catch (e) {
      setRunning(false);
      alert('Failed to start simulation.');
    }
  };

  const MetricBox = ({ label, value, color }) => (
    <div style={{ textAlign: 'center', padding: '14px 10px', background: (color || '#3b82f6') + '10',
      borderRadius: 8, border: `1px solid ${color || '#3b82f6'}20` }}>
      <div style={{ fontSize: 22, fontWeight: 700, color: color || '#3b82f6' }}>{value}</div>
      <div style={{ fontSize: 11, color: '#64748b', marginTop: 3 }}>{label}</div>
    </div>
  );

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ margin: 0, fontSize: 24, fontWeight: 700, color: '#0f172a' }}>Monte Carlo Simulations</h1>
        <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: 14 }}>Run thousands of scenarios to quantify supply chain risk</p>
      </div>

      <div style={{ background: 'linear-gradient(135deg, #1e3a5f, #0f172a)', borderRadius: 14,
        padding: 28, marginBottom: 28, color: '#fff' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
          <Zap size={20} color="#60a5fa" />
          <h3 style={{ margin: 0, fontSize: 17, fontWeight: 600 }}>Launch New Simulation</h3>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr auto auto', gap: 14, alignItems: 'flex-end' }}>
          <div>
            <label style={{ display: 'block', fontSize: 12, color: '#94a3b8', marginBottom: 6, fontWeight: 500 }}>Simulation Name</label>
            <input value={simName} onChange={e => setSimName(e.target.value)}
              style={{ width: '100%', padding: '10px 14px', borderRadius: 8, border: '1px solid #334155',
                background: '#1e293b', color: '#fff', fontSize: 14, boxSizing: 'border-box' }} />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: 12, color: '#94a3b8', marginBottom: 6, fontWeight: 500 }}>Iterations</label>
            <select value={iterations} onChange={e => setIterations(e.target.value)}
              style={{ padding: '10px 14px', borderRadius: 8, border: '1px solid #334155',
                background: '#1e293b', color: '#fff', fontSize: 14 }}>
              {[1000, 5000, 10000, 50000].map(n => <option key={n} value={n}>{n.toLocaleString()}</option>)}
            </select>
          </div>
          <button onClick={handleRun} disabled={running}
            style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 24px',
              background: running ? '#334155' : '#3b82f6', color: '#fff', border: 'none',
              borderRadius: 8, fontSize: 14, fontWeight: 600, cursor: running ? 'not-allowed' : 'pointer' }}>
            <Play size={15} />
            {running ? 'Running…' : 'Run Simulation'}
          </button>
        </div>
        <div style={{ marginTop: 16, fontSize: 12, color: '#64748b' }}>
          Includes 3 scenarios: Supplier Failure · Demand Surge · Shipping Delays
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        {simulations.length === 0 && (
          <div style={{ textAlign: 'center', padding: 60, color: '#94a3b8' }}>No simulations yet. Run your first one above!</div>
        )}
        {simulations.map(sim => {
          const baseline = sim.results?.baseline;
          const isExpanded = expanded === sim.id;
          return (
            <div key={sim.id} style={{ background: '#fff', borderRadius: 12, boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
              <div style={{ display: 'flex', alignItems: 'center', padding: '16px 20px', cursor: 'pointer', justifyContent: 'space-between' }}
                onClick={() => setExpanded(isExpanded ? null : sim.id)}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, padding: '4px 10px',
                    borderRadius: 20, background: (statusColor[sim.status] || '#94a3b8') + '15',
                    color: statusColor[sim.status], fontSize: 12, fontWeight: 600 }}>
                    {statusIcon[sim.status]} {sim.status}
                  </span>
                  <div>
                    <div style={{ fontWeight: 600, color: '#0f172a', fontSize: 15 }}>{sim.name}</div>
                    <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>
                      {sim.num_iterations.toLocaleString()} iterations · {new Date(sim.created_at).toLocaleString()}
                    </div>
                  </div>
                </div>
                {baseline && (
                  <div style={{ display: 'flex', gap: 24, alignItems: 'center' }}>
                    {[
                      { label: 'On Time', value: Math.round(baseline.on_time_probability * 100) + '%', color: '#22c55e' },
                      { label: 'Shortage', value: Math.round(baseline.shortage_probability * 100) + '%', color: '#f59e0b' },
                      { label: 'Severe', value: Math.round(baseline.severe_disruption_probability * 100) + '%', color: '#ef4444' },
                    ].map(({ label, value, color }) => (
                      <div key={label} style={{ textAlign: 'center' }}>
                        <div style={{ fontWeight: 700, color, fontSize: 18 }}>{value}</div>
                        <div style={{ fontSize: 11, color: '#94a3b8' }}>{label}</div>
                      </div>
                    ))}
                    {isExpanded ? <ChevronUp size={18} color="#94a3b8" /> : <ChevronDown size={18} color="#94a3b8" />}
                  </div>
                )}
              </div>
              {isExpanded && baseline && (
                <div style={{ borderTop: '1px solid #f1f5f9', padding: 24, background: '#fafafa' }}>
                  <h4 style={{ margin: '0 0 16px', fontSize: 14, fontWeight: 600 }}>Baseline Results</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 24 }}>
                    <MetricBox label="Service Level" value={Math.round(baseline.service_level * 100) + '%'} color="#22c55e" />
                    <MetricBox label="Risk Exposure" value={baseline.risk_exposure_score + '/100'} color="#f59e0b" />
                    <MetricBox label="Shortage Cost" value={'$' + baseline.expected_shortage_cost_usd?.toLocaleString()} color="#ef4444" />
                    <MetricBox label="Avg Shortage Units" value={baseline.avg_shortage_units_per_run} color="#8b5cf6" />
                  </div>
                  {sim.results?.scenarios && Object.keys(sim.results.scenarios).length > 0 && (
                    <>
                      <h4 style={{ margin: '0 0 16px', fontSize: 14, fontWeight: 600 }}>Scenario Comparison</h4>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
                        {Object.entries(sim.results.scenarios).map(([name, sc]) => (
                          <div key={name} style={{ background: '#fff', borderRadius: 10, padding: 16, border: '1px solid #e2e8f0' }}>
                            <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 12 }}>{name}</div>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                              <div style={{ textAlign: 'center', padding: 8, background: '#f0fdf4', borderRadius: 6 }}>
                                <div style={{ fontWeight: 700, color: '#22c55e' }}>{Math.round(sc.on_time_probability * 100)}%</div>
                                <div style={{ fontSize: 10, color: '#64748b' }}>On Time</div>
                              </div>
                              <div style={{ textAlign: 'center', padding: 8, background: '#fef2f2', borderRadius: 6 }}>
                                <div style={{ fontWeight: 700, color: '#ef4444' }}>{Math.round(sc.severe_disruption_probability * 100)}%</div>
                                <div style={{ fontSize: 10, color: '#64748b' }}>Severe</div>
                              </div>
                            </div>
                            <div style={{ marginTop: 10, fontSize: 12, color: '#64748b', textAlign: 'center' }}>
                              Risk: <span style={{ fontWeight: 600, color: '#f59e0b' }}>{sc.risk_exposure_score}/100</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}