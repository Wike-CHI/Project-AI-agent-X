# React Native Desktop 架构设计

## 1. 技术栈架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    React Native Desktop 架构                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    共享代码层 (~80%)                     │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │   │
│  │  │ UI组件   │ │ 状态管理 │ │ API客户端 │ │ 业务逻辑 │   │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐             │
│         ▼                    ▼                    ▼             │
│  ┌────────────┐      ┌────────────┐      ┌────────────┐        │
│  │ iOS        │      │ Android    │      │ Windows    │        │
│  │ react-     │      │ react-     │      │ react-     │        │
│  │ native     │      │ native     │      │ native     │        │
│  └────────────┘      └────────────┘      └────────────┘        │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐             │
│         ▼                    ▼                    ▼             │
│  ┌────────────┐      ┌────────────┐      ┌────────────┐        │
│  │ macOS      │      │ Web (PWA)  │      │ Linux      │        │
│  │ react-     │      │ React +    │      │ Tauri      │        │
│  │ native     │      │ Vite       │      │ (备选)     │        │
│  └────────────┘      └────────────┘      └────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 2. 技术选型详情

| 层次 | 技术 | 版本要求 | 用途 |
|-----|------|---------|------|
| **核心框架** | React Native | 0.75+ | 跨平台 UI 框架 |
| **桌面支持** | React Native Windows | 0.75+ | Windows 桌面应用 |
| **桌面支持** | React Native macOS | 0.75+ | macOS 桌面应用 |
| **状态管理** | Zustand | 4.x | 轻量状态管理 |
| **导航** | React Navigation | 6.x | 页面路由 |
| **HTTP 客户端** | Axios / Fetch | - | 网络请求 |
| **本地存储** | MMKV / SQLite | - | 离线数据存储 |
| **动画** | Lottie / Reanimated | - | 伴侣形象动画 |
| **3D 渲染** | Three.js / React Three Fiber | - | Web 3D 形象 |

## 3. 平台兼容策略

| 功能 | iOS | Android | Windows | macOS | Web | Linux |
|-----|-----|---------|---------|-------|-----|-------|
| 对话界面 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 伴侣形象 | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| 推送通知 | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| 本地存储 | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ |
| 后台任务 | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| 深色模式 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 生物识别 | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |

## 4. 伴侣形象渲染策略

```typescript
// frontend/src/components/companion/CompanionRenderer.tsx

import { Platform } from 'react-native';

type PlatformType = 'ios' | 'android' | 'windows' | 'macos' | 'web' | 'linux';

const getPlatform = (): PlatformType => {
  switch (Platform.OS) {
    case 'ios': return 'ios';
    case 'android': return 'android';
    case 'windows': return 'windows';
    case 'macos': return 'macos';
    default:
      if (Platform.OS === 'web' || typeof window !== 'undefined') {
        return 'web';
      }
      return 'linux';
  }
};

export const CompanionRenderer = ({ companionId }: { companionId: string }) => {
  const platform = getPlatform();

  switch (platform) {
    case 'ios':
    case 'android':
    case 'windows':
    case 'macos':
      return <LottieCompanion companionId={companionId} />;

    case 'web':
      return <WebGLCompanion companionId={companionId} />;

    case 'linux':
      return <Canvas2DCompanion companionId={companionId} />;

    default:
      return <TextCompanion companionId={companionId} />;
  }
};

// Lottie 动画组件 (移动端和桌面端)
const LottieCompanion = ({ companionId }: { companionId: string }) => {
  const animationSource = getCompanionAnimation(companionId);

  return (
    <LottieView
      source={animationSource}
      autoPlay
      loop
      style={{ width: 200, height: 200 }}
    />
  );
};

// WebGL 3D 组件 (Web 端)
const WebGLCompanion = ({ companionId }: { companionId: string }) => {
  return (
    <Canvas>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      <Companion3DModel companionId={companionId} />
    </Canvas>
  );
};

// Canvas 2D 降级组件 (Linux)
const Canvas2DCompanion = ({ companionId }: { companionId: string }) => {
  return (
    <View style={styles.canvasContainer}>
      <CompanionCanvas2D companionId={companionId} />
    </View>
  );
};
```

## 5. 状态管理

```typescript
// frontend/src/store/index.ts

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

// 用户状态
interface UserState {
  user: User | null;
  isAuthenticated: boolean;
  accessToken: string | null;
  refreshToken: string | null;
  setUser: (user: User) => void;
  setTokens: (access: string, refresh: string) => void;
  logout: () => void;
}

export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      accessToken: null,
      refreshToken: null,
      setUser: (user) => set({ user, isAuthenticated: true }),
      setTokens: (access, refresh) => set({ accessToken: access, refreshToken: refresh }),
      logout: () => set({ user: null, isAuthenticated: false, accessToken: null, refreshToken: null }),
    }),
    {
      name: 'user-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);

// 对话状态
interface ChatState {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  messages: Message[];
  isLoading: boolean;
  // ... actions
}

export const useChatStore = create<ChatState>((set) => ({
  conversations: [],
  currentConversation: null,
  messages: [],
  isLoading: false,
  // ... implementations
}));

// 记忆状态
interface MemoryState {
  memories: Memory[];
  isIndexed: boolean;
  // ... actions
}
```

## 6. API 服务层

```typescript
// frontend/src/services/api.ts

import axios, { AxiosInstance, AxiosError } from 'axios';
import { useUserStore } from '../store';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: process.env.API_BASE_URL || 'http://localhost:8000/api/v1',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // 请求拦截器 - 添加 Token
    this.client.interceptors.request.use(
      (config) => {
        const token = useUserStore.getState().accessToken;
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // 响应拦截器 - Token 刷新
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && originalRequest) {
          const refreshToken = useUserStore.getState().refreshToken;

          if (refreshToken) {
            try {
              const response = await axios.post('/auth/refresh', {
                refresh_token: refreshToken,
              });

              const { access_token } = response.data;
              useUserStore.getState().setTokens(access_token, refreshToken);

              originalRequest.headers.Authorization = `Bearer ${access_token}`;
              return this.client(originalRequest);
            } catch (refreshError) {
              useUserStore.getState().logout();
              return Promise.reject(refreshError);
            }
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // 对话 API
  async sendMessage(conversationId: string, message: string): Promise<Message> {
    const response = await this.client.post(`/conversations/${conversationId}/messages`, {
      content: message,
    });
    return response.data;
  }

  // 流式对话
  async *sendMessageStream(conversationId: string, message: string) {
    const response = await this.client.post(
      `/conversations/${conversationId}/messages/stream`,
      { content: message },
      { responseType: 'stream' }
    );

    const stream = response.data;
    const reader = stream.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      for (const line of chunk.split('\n')) {
        if (line.startsWith('data: ')) {
          yield JSON.parse(line.slice(6));
        }
      }
    }
  }

  // 记忆 API
  async searchMemories(query: string): Promise<Memory[]> {
    const response = await this.client.get('/memories/search', {
      params: { q: query },
    });
    return response.data;
  }
}

export const api = new ApiClient();
```

## 7. 项目结构

```
frontend/
├── index.jsx                 # Web 入口 (Vite)
├── App.tsx                   # RN iOS/Android/Windows/macOS 入口
├── app.json                  # RN 配置
│
├── src/
│   ├── components/           # 共享组件
│   │   ├── companion/        # 伴侣形象组件
│   │   │   ├── index.tsx
│   │   │   ├── CompanionRenderer.tsx
│   │   │   ├── LottieCompanion.tsx
│   │   │   ├── WebGLCompanion.tsx
│   │   │   └── animations/   # Lottie 动画文件
│   │   ├── chat/             # 对话组件
│   │   │   ├── MessageBubble.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   └── ConversationList.tsx
│   │   ├── memory/           # 记忆管理组件
│   │   ├── common/           # 通用组件
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   └── Modal.tsx
│   │   └── index.ts
│   │
│   ├── screens/              # 页面
│   │   ├── Home/
│   │   │   ├── index.tsx
│   │   │   └── styles.ts
│   │   ├── Chat/
│   │   │   ├── index.tsx
│   │   │   └── styles.ts
│   │   ├── Memories/
│   │   ├── Settings/
│   │   └── Auth/
│   │
│   ├── services/             # API 服务
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   ├── memory.ts
│   │   └── llm.ts
│   │
│   ├── store/                # 状态管理
│   │   ├── index.ts
│   │   ├── userStore.ts
│   │   ├── chatStore.ts
│   │   └── memoryStore.ts
│   │
│   ├── hooks/                # 自定义 Hooks
│   │   ├── useAuth.ts
│   │   ├── useChat.ts
│   │   ├── useMemory.ts
│   │   └── usePlatform.ts
│   │
│   ├── utils/                # 工具函数
│   │   ├── helpers.ts
│   │   ├── validators.ts
│   │   └── constants.ts
│   │
│   ├── assets/               # 静态资源
│   │   ├── images/
│   │   ├── animations/
│   │   └── fonts/
│   │
│   ├── styles/               # 全局样式
│   │   ├── theme.ts
│   │   └── globalStyles.ts
│   │
│   └── types/                # TypeScript 类型
│       ├── user.ts
│       ├── message.ts
│       ├── memory.ts
│       └── index.ts
│
├── windows/                  # RN Windows
│   └── pdns/
│       ├── Package.appxmanifest
│       ├── pch.h
│       └── pdns.vcxproj
│
├── macos/                    # RN macOS
│   └── pdns/
│       ├── Info.plist
│       ├── AppDelegate.mm
│       └── main.m
│
├── android/                  # RN Android
│   └── ...
│
├── ios/                      # RN iOS
│   └── ...
│
├── package.json
├── tsconfig.json
├── babel.config.js
├── metro.config.js
├── vite.config.ts            # Web 构建配置
└── README.md
```

## 8. 平台特定配置

### 8.1 React Native Windows

```json
// windows/pdns/Package.appxmanifest
{
  "$schema": "https://schemas.microsoft.com/developer/appx/2017/TargetDeviceFamily",
  "Identity": {
    "Name": "PDNS",
    "Publisher": "CN=PDNS"
  },
  "Properties": {
    "DisplayName": "Personal Digital Nervous System",
    "PublisherDisplayName": "PDNS",
    "Description": "AI Companion with long-term memory",
    "BackgroundColor": "#1E1E1E",
    "ForegroundText": "light"
  },
  "Dependencies": {
    "Microsoft.WindowsCppRuntimeLibrary": "10.0.22621.0",
    "Microsoft.VCLibs.140.00": "14.0"
  }
}
```

### 8.2 Web PWA 配置

```json
// public/manifest.json
{
  "name": "Personal Digital Nervous System",
  "short_name": "PDNS",
  "description": "AI Companion with long-term memory",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#1E1E1E",
  "theme_color": "#6366F1",
  "icons": [
    {
      "src": "/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

## 9. 构建命令

```bash
# 安装依赖
npm install

# iOS
cd ios && pod install && cd ..
npm run ios

# Android
npm run android

# Windows
npm run windows

# macOS
npm run macos

# Web (Vite)
npm run web

# 同时运行多个平台
npm run dev:all

# 构建生产版本
npm run build:ios
npm run build:android
npm run build:windows
npm run build:web
```
