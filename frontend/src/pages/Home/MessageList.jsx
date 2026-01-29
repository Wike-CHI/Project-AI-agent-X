import { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';

export default function MessageList({ messages, isTyping }) {
  const messagesEndRef = useRef(null);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  return (
    <div className="messages-container">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}

      {/* 打字指示器 */}
      {isTyping && (
        <div className="message companion-message companion-message-enhanced streaming-text">
          <div
            className="avatar avatar-sm companion-avatar"
            style={{ background: 'linear-gradient(135deg, #7C3AED 0%, #8B5CF6 100%)' }}
          >
            艾
          </div>
          <div className="message-content">
            <p className="message-text typing-cursor">我收到了你的消息，让我想想...</p>
            <div className="typing-indicator">
              <span>正在输入</span>
              <div className="typing-dots">
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
              </div>
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}
