import { createBrowserRouter } from 'react-router';
import App from '../App';
import { MainLayout } from '../components/layout/MainLayout';

// 懒加载页面组件
const Home = () => import('../pages/Home').then(m => ({ Component: m.default }));
const Memory = () => import('../pages/Memory').then(m => ({ Component: m.default }));
const Schedule = () => import('../pages/Schedule').then(m => ({ Component: m.default }));
const Store = () => import('../pages/Store').then(m => ({ Component: m.default }));
const Personality = () => import('../pages/Personality').then(m => ({ Component: m.default }));
const Settings = () => import('../pages/Settings').then(m => ({ Component: m.default }));

// 路由配置
export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        element: <MainLayout />,
        children: [
          {
            index: true,
            lazy: Home,
          },
          {
            path: 'memory',
            lazy: Memory,
          },
          {
            path: 'schedule',
            lazy: Schedule,
          },
          {
            path: 'store',
            lazy: Store,
          },
          {
            path: 'personality',
            lazy: Personality,
          },
          {
            path: 'settings',
            lazy: Settings,
          },
        ],
      },
    ],
  },
]);
