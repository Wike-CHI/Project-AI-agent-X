import { Outlet, useLocation } from 'react-router';
import { Sidebar } from './Sidebar';

export function MainLayout() {
  const location = useLocation();

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <div key={location.pathname} className="page-content">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
