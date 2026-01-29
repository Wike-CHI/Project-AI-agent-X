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
        // 主色系 - AI Indigo (更柔和、专业)
        primary: {
          DEFAULT: '#6366F1', // Indigo-500
          hover: '#4F46E5',   // Indigo-600
          light: '#EEF2FF',   // Indigo-50
          50: '#EEF2FF',
          100: '#E0E7FF',
          200: '#C7D2FE',
          300: '#A5B4FC',
          400: '#818CF8',
          500: '#6366F1',
          600: '#4F46E5',
          700: '#4338CA',
          800: '#3730A3',
          900: '#312E81',
          950: '#1E1B4B',
        },
        // 辅助色 - Teal (护眼、现代)
        secondary: {
          DEFAULT: '#14B8A6', // Teal-500
          hover: '#0D9488',   // Teal-600
          light: '#CCFBF1',   // Teal-50
          50: '#F0FDFA',
          100: '#CCFBF1',
          200: '#99F6E4',
          300: '#5EEAD4',
          400: '#2DD4BF',
          500: '#14B8A6',
          600: '#0D9488',
          700: '#0F766E',
          800: '#115E59',
          900: '#134E4A',
          950: '#042F2E',
        },
        // CTA 青色 (保持原有但优化)
        cta: {
          DEFAULT: '#06B6D4', // Cyan-500
          hover: '#0891B2',   // Cyan-600
          light: '#CFFAFE',   // Cyan-50
          50: '#ECFEFF',
          100: '#CFFAFE',
          200: '#A5F3FC',
          300: '#67E8F9',
          400: '#22D3EE',
          500: '#06B6D4',
          600: '#0891B2',
          700: '#0E7490',
          800: '#155E75',
          900: '#164E63',
          950: '#083344',
        },
        // 功能色
        success: {
          DEFAULT: '#10B981', // Emerald-500
          light: '#D1FAE5',   // Emerald-100
        },
        warning: {
          DEFAULT: '#F59E0B', // Amber-500
          light: '#FEF3C7',   // Amber-100
        },
        error: {
          DEFAULT: '#EF4444', // Red-500
          light: '#FEE2E2',   // Red-100
        },
        info: {
          DEFAULT: '#3B82F6', // Blue-500
          light: '#DBEAFE',   // Blue-100
        },
        // 背景色和前景色
        background: '#FFFFFF',
        foreground: '#0F172A', // Slate-900
        // 文字颜色
        'text-primary': '#0F172A',   // Slate-900
        'text-secondary': '#475569', // Slate-600
        'text-muted': '#94A3B8',     // Slate-400
        'text-light': '#CBD5E1',     // Slate-300
        // 边框和输入框
        border: '#E2E8F0', // Slate-200
        input: '#E2E8F0',
        ring: '#6366F1',   // 匹配新的 primary
      },
      borderRadius: {
        sm: '8px',
        md: '12px',
        lg: '16px',
        xl: '20px',
      },
      boxShadow: {
        sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        md: '0 2px 8px 0 rgba(99, 102, 241, 0.08)',
        lg: '0 8px 16px -4px rgba(99, 102, 241, 0.12)',
        xl: '0 12px 24px -8px rgba(99, 102, 241, 0.15)',
        'primary': '0 4px 12px rgba(99, 102, 241, 0.25)',
        'secondary': '0 4px 12px rgba(20, 184, 166, 0.25)',
        'cta': '0 4px 12px rgba(6, 182, 212, 0.3)',
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
