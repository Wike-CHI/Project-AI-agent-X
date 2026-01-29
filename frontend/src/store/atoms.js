import { atom } from 'jotai';

// 用户信息
export const userAtom = atom({
  name: '张三',
  email: 'zhang***@email.com',
  avatar: '张',
});

// 伴侣信息
export const companionAtom = atom({
  name: '小艾',
  status: 'online',
  avatar: '艾',
});

// 对话状态
export const messagesAtom = atom([
  {
    id: 1,
    type: 'companion',
    content: '嗨！今天过得怎么样？有什么可以帮你的？',
    isTyping: false,
    emotion: null,
  },
  {
    id: 2,
    type: 'user',
    content: '我今天工作有点累，想聊聊天',
  },
  {
    id: 3,
    type: 'companion',
    content: '听起来你今天压力很大呢，要不要和我分享一下？',
    isTyping: false,
    emotion: '关心',
  },
]);

export const isTypingAtom = atom(false);
export const currentInputAtom = atom('');

// 记忆状态
export const memoriesAtom = atom([
  {
    id: 1,
    type: 'episodic',
    title: '情景记忆',
    content: '1月27日聊到想学西班牙语',
    date: '2024-01-27',
    tags: ['学习'],
  },
  {
    id: 2,
    type: 'semantic',
    title: '语义记忆',
    content: '用户最喜欢美式咖啡',
    date: '长期记忆',
    tags: ['偏好'],
  },
  {
    id: 3,
    type: 'episodic',
    title: '情景记忆',
    content: '今天开了一天的项目评审会议，感觉很累',
    date: '2024-01-29',
    tags: ['工作'],
  },
]);

export const memoryFilterAtom = atom({
  search: '',
  types: ['episodic', 'semantic'],
});

// 日程状态
export const schedulesAtom = atom([
  {
    id: 1,
    title: '项目周会',
    time: '09:00',
    date: '2024-01-29',
    type: 'normal',
  },
  {
    id: 2,
    title: '产品评审',
    time: '14:00',
    date: '2024-01-29',
    type: 'warning',
  },
  {
    id: 3,
    title: 'AI建议：适当休息',
    time: '10:30',
    date: '2024-01-29',
    type: 'ai-suggestion',
  },
]);

export const selectedDateAtom = atom(new Date());

// 智能体商店
export const agentsAtom = atom([
  {
    id: 1,
    name: '财务助手',
    description: '专业的理财建议和财务规划',
    rating: 4.8,
    icon: '💰',
    tags: ['财务', '专业'],
    installed: false,
  },
  {
    id: 2,
    name: '创意写手',
    description: '帮助你完成各种创意写作任务',
    rating: 4.9,
    icon: '✍️',
    tags: ['写作', '创意'],
    installed: true,
  },
  {
    id: 3,
    name: '数据分析',
    description: '强大的数据分析和可视化能力',
    rating: 4.7,
    icon: '📊',
    tags: ['数据', '分析'],
    installed: false,
  },
  {
    id: 4,
    name: '健康顾问',
    description: '专业的健康建议和生活指导',
    rating: 4.6,
    icon: '🏥',
    tags: ['健康', '生活'],
    installed: false,
  },
]);

export const myAgentsAtom = atom([2]);

// 性格参数
export const personalityAtom = atom({
  empathy: 70,
  humor: 85,
  seriousness: 55,
  proactive: 90,
});

// 设置
export const settingsAtom = atom({
  theme: 'system',
  fontSize: 'default',
  llmModel: 'MiniMax',
  temperature: 0.7,
  apiKey: '••••••••••••••••',
  localProcessing: true,
  endToEndEncryption: true,
  memoryRetention: 30,
  companionPosition: 'left',
});
