import { atom } from 'jotai';
import { messagesAtom, currentInputAtom, isTypingAtom, personalityAtom } from './atoms';

// 发送消息的派生atom
export const sendMessageAtom = atom(
  null,
  (get, set, message) => {
    // 添加用户消息
    const newMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
    };
    set(messagesAtom, [...get(messagesAtom), newMessage]);

    // 清空输入框
    set(currentInputAtom, '');

    // 设置打字状态
    set(isTypingAtom, true);

    // 模拟AI回复（1秒后）
    setTimeout(() => {
      const aiMessage = {
        id: Date.now() + 1,
        type: 'companion',
        content: `我收到了你的消息："${message}"。让我想想...`,
        isTyping: false,
        emotion: null,
      };
      set(messagesAtom, prev => [...prev, aiMessage]);
      set(isTypingAtom, false);
    }, 1000);
  }
);

// 更新性格参数的派生atom
export const updatePersonalityAtom = atom(
  null,
  (get, set, updates) => {
    const current = get(personalityAtom);
    set(personalityAtom, { ...current, ...updates });
  }
);
