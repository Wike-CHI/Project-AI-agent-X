import { useState } from 'react';
import { Mic } from 'lucide-react';
import { useAtom } from 'jotai';
import { currentInputAtom } from '../../store/atoms';
import { sendMessageAtom } from '../../store/actions';

export default function ChatInput() {
  const [input, setInput] = useState('');
  const [, setCurrentInput] = useAtom(currentInputAtom);
  const [, sendMessage] = useAtom(sendMessageAtom);

  const handleSend = () => {
    if (input.trim()) {
      sendMessage(input.trim());
      setInput('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="input-area">
      <button className="btn btn-icon btn-secondary">
        <Mic />
      </button>
      <input
        type="text"
        className="chat-input"
        value={input}
        onChange={(e) => {
          setInput(e.target.value);
          setCurrentInput(e.target.value);
        }}
        onKeyPress={handleKeyPress}
        placeholder="输入消息..."
      />
      <button className="btn btn-cta send-btn" onClick={handleSend}>
        发送
      </button>
    </div>
  );
}
