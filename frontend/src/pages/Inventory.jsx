import { useEffect, useState } from 'react';
import { getInventory, getProducts, getWarehouses, getSuppliers, createInventory } from '../api/endpoints';
import { Plus, Package } from 'lucide-react';

const riskColors = { critical: '#ef4444', high: '#f59e0b', medium: '#3b82f6', low: '#22c55e' };

export default function Inventory() {
  const [inventory, setInventory] = useState([]);
  const [products, setProducts] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ product_id: '', warehouse_id: '', supplier_id: '',
    current_stock: 100, reorder_point: 50, safety_stock: 20, max_stock: 500 });

  const load = () => Promise.all([getInventory(), getProducts(), getWarehouses(), getSuppliers()])
    .then(([inv, prod, wh, sup]) => {
      setInventory(inv.data); setProducts(prod.data);
      setWarehouses(wh.data); setSuppliers(sup.data);
    });

  useEffect(() => { load(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    await createInventory({ ...form, product_id: +form.product_id, warehouse_id: +form.warehouse_id,
      supplier_id: form.supplier_id ? +form.supplier_id : null,
      current_stock: +form.current_stock, reorder_point: +form.reorder_point,
      safety_stock: +form.safety_stock, max_stock: +form.max_stock });
    setShowForm(false); load();
  };

  const getProductName = (id) => products.find(p => p.id === id)?.name || `Product ${id}`;
  const getWarehouseName = (id) => warehouses.find(w => w.id === id)?.name || `Warehouse ${id}`;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 24, fontWeight: 700, color: '#0f172a' }}>Inventory</h1>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: 14 }}>Stock levels and health monitoring</p>
        </div>
        <button onClick={() => setShowForm(!showForm)}
          style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 18px',
            background: '#2563eb', color: '#fff', border: 'none', borderRadius: 8,
            fontSize: 14, fontWeight: 600, cursor: 'pointer' }}>
          <Plus size={16} /> Add Item
        </button>
      </div>

      {showForm && (
        <div style={{ background: '#fff', borderRadius: 12, padding: 24, marginBottom: 24,
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h3 style={{ margin: '0 0 20px', fontSize: 16, fontWeight: 600 }}>Add Inventory Item</h3>
          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
              {[
                { label: 'Product *', key: 'product_id', type: 'select', options: products.map(p => ({ value: p.id, label: p.name })) },
                { label: 'Warehouse *', key: 'warehouse_id', type: 'select', options: warehouses.map(w => ({ value: w.id, label: w.name })) },
                { label: 'Supplier', key: 'supplier_id', type: 'select', options: [{ value: '', label: 'None' }, ...suppliers.map(s => ({ value: s.id, label: s.name }))] },
                { label: 'Current Stock', key: 'current_stock', type: 'number' },
                { label: 'Reorder Point', key: 'reorder_point', type: 'number' },
                { label: 'Safety Stock', key: 'safety_stock', type: 'number' },
              ].map(({ label, key, type, options }) => (
                <div key={key}>
                  <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#374151', marginBottom: 6 }}>{label}</label>
                  {type === 'select' ? (
                    <select value={form[key]} onChange={e => setForm({ ...form, [key]: e.target.value })}
                      style={{ width: '100%', padding: '9px 12px', border: '1px solid #d1d5db', borderRadius: 7, fontSize: 13 }}>
                      {options?.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                    </select>
                  ) : (
                    <input type={type} value={form[key]} onChange={e => setForm({ ...form, [key]: e.target.value })}
                      style={{ width: '100%', padding: '9px 12px', border: '1px solid #d1d5db',
                        borderRadius: 7, fontSize: 13, boxSizing: 'border-box' }} />
                  )}
                </div>
              ))}
            </div>
            <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>
              <button type="submit" style={{ padding: '9px 20px', background: '#2563eb', color: '#fff',
                border: 'none', borderRadius: 7, fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>Save</button>
              <button type="button" onClick={() => setShowForm(false)}
                style={{ padding: '9px 20px', background: '#f1f5f9', color: '#475569',
                  border: 'none', borderRadius: 7, fontSize: 13, cursor: 'pointer' }}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      <div style={{ background: '#fff', borderRadius: 12, boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
        {inventory.length === 0 ? (
          <div style={{ padding: 60, textAlign: 'center', color: '#94a3b8' }}>
            <Package size={40} style={{ opacity: 0.3, marginBottom: 12 }} />
            <p style={{ margin: 0 }}>No inventory items yet.</p>
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                {['Product', 'Warehouse', 'Stock', 'Reorder Pt', 'Days of Stock', 'Risk'].map(h => (
                  <th key={h} style={{ padding: '12px 16px', textAlign: 'left', fontSize: 12,
                    fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {inventory.map((inv, i) => {
                const color = riskColors[inv.stockout_risk] || '#94a3b8';
                return (
                  <tr key={inv.id} style={{ borderBottom: '1px solid #f1f5f9', background: i % 2 === 0 ? '#fff' : '#fafafa' }}>
                    <td style={{ padding: '14px 16px', fontWeight: 600, color: '#0f172a', fontSize: 14 }}>{getProductName(inv.product_id)}</td>
                    <td style={{ padding: '14px 16px', color: '#64748b', fontSize: 13 }}>{getWarehouseName(inv.warehouse_id)}</td>
                    <td style={{ padding: '14px 16px', fontWeight: 600, color: '#0f172a' }}>{inv.current_stock}</td>
                    <td style={{ padding: '14px 16px', color: '#64748b', fontSize: 13 }}>{inv.reorder_point}</td>
                    <td style={{ padding: '14px 16px', color: '#0f172a', fontSize: 13 }}>{inv.days_of_stock ?? '—'}d</td>
                    <td style={{ padding: '14px 16px' }}>
                      <span style={{ padding: '3px 10px', borderRadius: 20, background: color + '15',
                        color, fontSize: 12, fontWeight: 600, textTransform: 'capitalize' }}>
                        {inv.stockout_risk ?? 'unknown'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
