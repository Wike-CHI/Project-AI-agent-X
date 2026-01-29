import { Link } from 'react-router';
import { Calendar, Brain } from 'lucide-react';

export default function WelcomeSection() {
  return (
    <div className="welcome-section">
      <h1 className="greeting-text">早上好，张三 👋</h1>
      <p className="status-summary">今天有3个日程，开始对话吧</p>
      <div className="quick-actions">
        <button className="btn btn-primary">
          <Calendar style={{ width: '16px', height: '16px' }} />
          日程
        </button>
        <button className="btn btn-primary">
          <Brain style={{ width: '16px', height: '16px' }} />
          记忆
        </button>
      </div>
    </div>
  );
}
