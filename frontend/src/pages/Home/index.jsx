import { useAtom } from 'jotai';
import { messagesAtom, isTypingAtom, companionAtom } from '../../store/atoms';
import WelcomeSection from './WelcomeSection';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import CompanionPanel from './CompanionPanel';
import './home.css';

export default function Home() {
  const [messages] = useAtom(messagesAtom);
  const [isTyping] = useAtom(isTypingAtom);
  const [companion] = useAtom(companionAtom);

  return (
    <div className="home-layout">
      {/* 左侧对话区域 */}
      <div className="chat-area">
        <WelcomeSection />
        <MessageList messages={messages} isTyping={isTyping} />
        <ChatInput />
      </div>

      {/* 右侧伴侣面板 */}
      <CompanionPanel companion={companion} />
    </div>
  );
}
