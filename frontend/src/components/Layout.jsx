import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Users, Package, Activity, LogOut, TrendingUp } from 'lucide-react';

const navItems = [
  { to: '/',            icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/suppliers',   icon: Users,           label: 'Suppliers' },
  { to: '/inventory',   icon: Package,         label: 'Inventory' },
  { to: '/simulations', icon: Activity,        label: 'Simulations' },
];

export default function Layout() {
  const navigate = useNavigate();
  const logout = () => { localStorage.removeItem('token'); navigate('/login'); };

  return (
    <div style={{ display: 'flex', height: '100vh', fontFamily: 'system-ui, sans-serif', background: '#f8fafc' }}>
      {/* Sidebar */}
      <aside style={{ width: 240, background: '#0f172a', color: '#fff', display: 'flex', flexDirection: 'column', padding: '24px 0' }}>
        <div style={{ padding: '0 24px 32px', borderBottom: '1px solid #1e293b' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <TrendingUp size={22} color="#3b82f6" />
            <div>
              <div style={{ fontWeight: 700, fontSize: 14 }}>Supply Chain</div>
              <div style={{ fontSize: 11, color: '#64748b' }}>Risk Platform</div>
            </div>
          </div>
        </div>

        <nav style={{ flex: 1, padding: '16px 12px' }}>
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink key={to} to={to} end={to === '/'}
              style={({ isActive }) => ({
                display: 'flex', alignItems: 'center', gap: 12,
                padding: '10px 12px', borderRadius: 8, marginBottom: 4,
                textDecoration: 'none', fontSize: 14, fontWeight: 500,
                color: isActive ? '#fff' : '#94a3b8',
                background: isActive ? '#1e40af' : 'transparent',
                transition: 'all 0.15s',
              })}>
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div style={{ padding: '16px 12px', borderTop: '1px solid #1e293b' }}>
          <button onClick={logout}
            style={{ display: 'flex', alignItems: 'center', gap: 12, width: '100%',
              padding: '10px 12px', borderRadius: 8, border: 'none', cursor: 'pointer',
              background: 'transparent', color: '#94a3b8', fontSize: 14, fontWeight: 500 }}>
            <LogOut size={18} /> Logout
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main style={{ flex: 1, overflow: 'auto', padding: 32 }}>
        <Outlet />
      </main>
    </div>
  );
}
