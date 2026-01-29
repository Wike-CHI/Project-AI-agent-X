import { Link, useLocation } from 'react-router';
import {
  MessageSquare,
  Brain,
  Calendar,
  Store,
  Smile,
  Settings,
} from 'lucide-react';

const navItems = [
  { path: '/', label: '对话', icon: MessageSquare },
  { path: '/memory', label: '记忆', icon: Brain },
  { path: '/schedule', label: '日程', icon: Calendar },
  { path: '/store', label: '商店', icon: Store },
  { path: '/personality', label: '性格', icon: Smile },
  { path: '/settings', label: '设置', icon: Settings },
];

export function Sidebar() {
  const location = useLocation();

  return (
    <aside className="w-60 glass shadow-lg flex flex-col gap-2 p-6 flex-shrink-0">
      {/* Logo */}
      <div className="flex items-center gap-3 h-16 mb-2">
        <div
          className="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold text-lg shadow-md"
          style={{ backgroundColor: '#7C3AED' }}
        >
          AI
        </div>
        <span className="text-xl font-semibold" style={{ color: '#171717' }}>
          AI 伴侣
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-2">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`
                flex items-center gap-3 p-3 rounded-lg transition-all duration-200 relative
                ${isActive
                  ? 'text-white shadow-md'
                  : 'hover:shadow-sm'
                }
              `}
              style={{
                backgroundColor: isActive ? '#7C3AED' : 'transparent',
                color: isActive ? '#FFFFFF' : '#404040',
              }}
              onMouseEnter={(e) => {
                if (!isActive) {
                  e.currentTarget.style.transform = 'translateX(4px)';
                  e.currentTarget.style.backgroundColor = '#EDE9FE';
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive) {
                  e.currentTarget.style.transform = 'translateX(0)';
                  e.currentTarget.style.backgroundColor = 'transparent';
                }
              }}
            >
              {/* Active indicator */}
              {isActive && (
                <div
                  className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 rounded-r"
                  style={{ backgroundColor: '#8B5CF6' }}
                />
              )}

              <Icon className="w-5 h-5" />
              <span className="text-base font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
