export default function MessageBubble({ message }) {
  const isCompanion = message.type === 'companion';

  return (
    <div
      className={`message ${isCompanion ? 'companion-message' : 'user-message'} ${
        isCompanion ? 'companion-message-enhanced' : 'user-message-enhanced'
      } streaming-text`}
    >
      {/* 头像 */}
      <div
        className={`avatar avatar-sm ${isCompanion ? 'companion-avatar' : 'user-avatar'}`}
        style={{
          background: isCompanion
            ? 'linear-gradient(135deg, #7C3AED 0%, #8B5CF6 100%)'
            : 'linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%)',
        }}
      >
        {isCompanion ? '艾' : '张'}
      </div>

      {/* 消息内容 */}
      <div className="message-content">
        <p className="message-text">{message.content}</p>

        {/* 情绪徽章 */}
        {message.emotion && (
          <span
            className="emotion-badge"
            style={{
              background: 'linear-gradient(135deg, #FCE7F3 0%, #FBCFE8 100%)',
              color: '#EC4899',
            }}
          >
            {message.emotion}
          </span>
        )}
      </div>
    </div>
  );
}
