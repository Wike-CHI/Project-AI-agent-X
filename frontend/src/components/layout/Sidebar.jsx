import { Link, useLocation } from 'react-router';
import {
  MessageSquare,
  Brain,
  Calendar,
  Store,
  Smile,
  Settings,
} from 'lucide-react';
import { useTheme } from 'next-themes';

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
  const { theme, resolvedTheme } = useTheme();

  // 判断实际的主题模式（如果是 'system'，则使用 resolvedTheme）
  const actualTheme = theme === 'system' ? resolvedTheme : theme;
  const isDark = actualTheme === 'dark';

  return (
    <aside className="w-60 glass shadow-lg flex flex-col gap-2 p-6 flex-shrink-0">
      {/* Logo */}
      <div className="flex items-center gap-3 h-16 mb-2">
        <div
          className="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold text-lg shadow-md"
          style={{
            background: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)',
          }}
        >
          AI
        </div>
        <span
          className="text-xl font-semibold"
          style={{
            color: isDark ? '#F8FAFC' : '#0F172A'
          }}
        >
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
              className="flex items-center gap-3 p-3 rounded-lg transition-all duration-200 relative"
              style={{
                backgroundColor: isActive ? '#6366F1' : 'transparent',
                color: isActive ? '#FFFFFF' : isDark ? '#CBD5E1' : '#475569',
                boxShadow: isActive ? '0 4px 6px rgba(99, 102, 241, 0.3)' : 'none',
              }}
              onMouseEnter={(e) => {
                if (!isActive) {
                  e.currentTarget.style.backgroundColor = isDark ? 'rgba(99, 102, 241, 0.2)' : '#EEF2FF';
                  e.currentTarget.style.color = '#6366F1';
                  e.currentTarget.style.transform = 'translateX(4px)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive) {
                  e.currentTarget.style.backgroundColor = 'transparent';
                  e.currentTarget.style.color = isDark ? '#CBD5E1' : '#475569';
                  e.currentTarget.style.transform = 'translateX(0)';
                }
              }}
            >
              {/* Active indicator */}
              {isActive && (
                <div
                  className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 rounded-r"
                  style={{ backgroundColor: '#A5B4FC' }}
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
