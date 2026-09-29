/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Modern Electric Primary - Indigo/Violet spectrum
        primary: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',   // Vivid indigo
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
          950: '#1e1b4b',
        },
        // Accent: Vivid Emerald for success states and positive actions
        accent: {
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#10b981',   // Emerald
          600: '#059669',
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
        },
        // Warm accent for highlights, warnings
        warm: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',   // Amber
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },
        // Priority Colors
        priority: {
          high: {
            bg: 'rgba(239, 68, 68, 0.1)',
            border: 'rgba(239, 68, 68, 0.25)',
            text: '#ef4444',
            icon: '#f87171',
          },
          medium: {
            bg: 'rgba(245, 158, 11, 0.1)',
            border: 'rgba(245, 158, 11, 0.25)',
            text: '#f59e0b',
            icon: '#fbbf24',
          },
          low: {
            bg: 'rgba(16, 185, 129, 0.1)',
            border: 'rgba(16, 185, 129, 0.25)',
            text: '#10b981',
            icon: '#34d399',
          },
        },
        // Status Colors
        status: {
          submitted: { bg: 'rgba(245, 158, 11, 0.1)', text: '#fbbf24', border: 'rgba(245, 158, 11, 0.25)' },
          prioritized: { bg: 'rgba(251, 146, 60, 0.1)', text: '#fb923c', border: 'rgba(251, 146, 60, 0.25)' },
          assigned: { bg: 'rgba(99, 102, 241, 0.1)', text: '#818cf8', border: 'rgba(99, 102, 241, 0.25)' },
          in_progress: { bg: 'rgba(59, 130, 246, 0.1)', text: '#60a5fa', border: 'rgba(59, 130, 246, 0.25)' },
          resolved: { bg: 'rgba(16, 185, 129, 0.1)', text: '#34d399', border: 'rgba(16, 185, 129, 0.25)' },
          rejected: { bg: 'rgba(239, 68, 68, 0.1)', text: '#f87171', border: 'rgba(239, 68, 68, 0.25)' },
        },
        // Surfaces: Deep dark with layered glass elevation
        surface: {
          DEFAULT: '#0f1729',       // Primary dark background
          elevated: '#0b1120',      // Deepest dark
          hover: '#1a2744',         // Hover surface
          card: '#141e35',          // Card background
          paper: '#1a2744',         // Lighter card
          glass: 'rgba(20, 30, 53, 0.8)',  // Glass panel
        },
        border: {
          DEFAULT: 'rgba(148, 163, 184, 0.12)',
          strong: 'rgba(148, 163, 184, 0.2)',
          subtle: 'rgba(148, 163, 184, 0.06)',
          glow: 'rgba(99, 102, 241, 0.3)',
        },
        text: {
          primary: '#f1f5f9',       // Bright white-ish
          secondary: '#94a3b8',     // Soft slate
          muted: '#64748b',         // Dim slate
          inverse: '#0f172a',
        },
      },
      fontFamily: {
        sans: ['"Inter"', '"Space Grotesk"', 'system-ui', '-apple-system', 'sans-serif'],
        heading: ['"Space Grotesk"', '"Inter"', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"Fira Code"', 'ui-monospace', 'monospace'],
      },
      fontSize: {
        'heading-xl': ['2.5rem', { lineHeight: '1.15', letterSpacing: '-0.03em', fontWeight: '700' }],
        'heading-lg': ['2rem', { lineHeight: '1.2', letterSpacing: '-0.025em', fontWeight: '700' }],
        'heading-md': ['1.5rem', { lineHeight: '1.3', letterSpacing: '-0.02em', fontWeight: '600' }],
        'heading-sm': ['1.25rem', { lineHeight: '1.35', letterSpacing: '-0.01em', fontWeight: '600' }],
        'body-lg': ['1.125rem', { lineHeight: '1.6' }],
        'body': ['1rem', { lineHeight: '1.6' }],
        'body-sm': ['0.875rem', { lineHeight: '1.5' }],
        'caption': ['0.75rem', { lineHeight: '1.5', letterSpacing: '0.03em' }],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      boxShadow: {
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(148, 163, 184, 0.06)',
        'card-hover': '0 4px 16px 0 rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(99, 102, 241, 0.15)',
        'elevated': '0 8px 32px 0 rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(148, 163, 184, 0.08)',
        'glow-primary': '0 0 20px rgba(99, 102, 241, 0.15), 0 0 60px rgba(99, 102, 241, 0.05)',
        'glow-accent': '0 0 20px rgba(16, 185, 129, 0.15), 0 0 60px rgba(16, 185, 129, 0.05)',
        'glow-warm': '0 0 20px rgba(245, 158, 11, 0.15), 0 0 60px rgba(245, 158, 11, 0.05)',
        'inner-glow': 'inset 0 1px 0 0 rgba(148, 163, 184, 0.05)',
      },
      borderRadius: {
        'card': '12px',
        'button': '10px',
        'input': '10px',
        'badge': '6px',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
        'slide-down': 'slideDown 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
        'pulse-soft': 'pulseSoft 2s infinite',
        'glow': 'glowPulse 3s ease-in-out infinite',
        'float': 'float 6s ease-in-out infinite',
        'shimmer': 'shimmer 2.5s linear infinite',
        'gradient-x': 'gradientX 15s ease infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(4px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideDown: {
          '0%': { opacity: '0', transform: 'translateY(-16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.6' },
        },
        glowPulse: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(99, 102, 241, 0.1)' },
          '50%': { boxShadow: '0 0 40px rgba(99, 102, 241, 0.25)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        gradientX: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'mesh-gradient': 'radial-gradient(at 40% 20%, rgba(99, 102, 241, 0.15) 0px, transparent 50%), radial-gradient(at 80% 0%, rgba(16, 185, 129, 0.08) 0px, transparent 50%), radial-gradient(at 0% 50%, rgba(245, 158, 11, 0.05) 0px, transparent 50%)',
      },
    },
  },
  plugins: [],
}