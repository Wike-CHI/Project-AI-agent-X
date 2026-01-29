import { Sparkles, Lightbulb } from 'lucide-react';

export default function CompanionPanel({ companion }) {
  return (
    <aside className="companion-panel">
      {/* 头像区 */}
      <div className="avatar-section card">
        <div
          className="avatar avatar-lg"
          style={{ background: 'linear-gradient(135deg, #7C3AED 0%, #8B5CF6 100%)' }}
        >
          {companion.avatar}
        </div>
        <h3 className="avatar-name">{companion.name}</h3>
        <p className="avatar-status ai-status-online">
          <span className="status-dot-enhanced"></span>
          在线 · 关注中
        </p>
      </div>

      {/* 快捷操作 */}
      <div className="quick-section">
        <h4 className="section-title">快捷操作</h4>
        <div className="quick-item">
          <Sparkles style={{ color: '#7C3AED', width: '18px', height: '18px' }} />
          <span>聊聊今天的心情</span>
        </div>
        <div className="quick-item">
          <Lightbulb style={{ color: '#F59E0B', width: '18px', height: '18px' }} />
          <span>获取建议</span>
        </div>
      </div>
    </aside>
  );
}
