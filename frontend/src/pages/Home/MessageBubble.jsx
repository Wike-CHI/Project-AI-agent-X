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
            ? 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)'
            : 'linear-gradient(135deg, #14B8A6 0%, #06B6D4 100%)',
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
              background: 'linear-gradient(135deg, #CCFBF1 0%, #CFFAFE 100%)',
              color: '#0D9488',
            }}
          >
            {message.emotion}
          </span>
        )}
      </div>
    </div>
  );
}
