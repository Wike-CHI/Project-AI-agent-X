/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class'],
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // AI紫色主题
        primary: {
          DEFAULT: '#7C3AED',
          hover: '#6D28D9',
          light: '#EDE9FE',
          50: '#FAF5FF',
          100: '#F5F3FF',
          200: '#EDE9FE',
          500: '#8B5CF6',
          600: '#7C3AED',
          700: '#6D28D9',
        },
        // CTA青色
        cta: {
          DEFAULT: '#06B6D4',
          hover: '#0891B2',
          light: '#CFFAFE',
        },
        // 功能色
        success: '#10B981',
        warning: '#F59E0B',
        error: '#EF4444',
        info: '#3B82F6',
        // 背景色
        background: '#FFFFFF',
        foreground: '#171717',
        // 文字颜色
        'text-primary': '#171717',
        'text-secondary': '#404040',
        'text-muted': '#737373',
        'text-light': '#A3A3A3',
        // 边框
        border: '#E5E5E5',
        input: '#E5E5E5',
        ring: '#7C3AED',
      },
      borderRadius: {
        sm: '8px',
        md: '12px',
        lg: '16px',
        xl: '20px',
      },
      boxShadow: {
        sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        md: '0 2px 8px 0 rgba(124, 58, 237, 0.08)',
        lg: '0 8px 16px -4px rgba(124, 58, 237, 0.12)',
        xl: '0 12px 24px -8px rgba(124, 58, 237, 0.15)',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
      },
      animation: {
        'flowing-gradient': 'flowingGradient 15s ease infinite',
        'pulse-slow': 'pulse 2s infinite',
        'typing': 'typing 1.5s steps(3) infinite',
      },
      keyframes: {
        flowingGradient: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        typing: {
          '0%, 60%, 100%': { opacity: '1' },
          '30%': { opacity: '0' },
        },
      },
    },
  },
  plugins: [],
}
