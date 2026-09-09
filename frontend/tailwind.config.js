/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Municipal Modern Palette
        primary: {
          50: '#f0f7fa',
          100: '#dceef5',
          200: '#b9dceb',
          300: '#85c3dc',
          400: '#4aa3c8',
          500: '#2d8ab4',  // Main primary - deep teal
          600: '#206f93',
          700: '#1b5773',
          800: '#18485d',
          900: '#163d4d',
          950: '#0d2530',
        },
        // Priority Colors - accessible (not color-only)
        priority: {
          high: {
            bg: '#fef3f2',
            border: '#fda29b',
            text: '#c0152f',
            icon: '#c0152f',
          },
          medium: {
            bg: '#fff8ed',
            border: '#fec84b',
            text: '#ad6800',
            icon: '#ad6800',
          },
          low: {
            bg: '#f0fdf4',
            border: '#86efac',
            text: '#166534',
            icon: '#166534',
          },
        },
        // Status Colors
        status: {
          submitted: { bg: '#eef2ff', text: '#3730a3', border: '#c7d2fe' },
          prioritized: { bg: '#fff7ed', text: '#9a3412', border: '#fed7aa' },
          assigned: { bg: '#f0fdf4', text: '#166534', border: '#bbf7d0' },
          in_progress: { bg: '#faf5ff', text: '#6b21a8', border: '#e9d5ff' },
          resolved: { bg: '#f0fdf4', text: '#166534', border: '#86efac' },
          rejected: { bg: '#fef2f2', text: '#991b1b', border: '#fecaca' },
        },
        surface: {
          DEFAULT: '#ffffff',
          elevated: '#f8fafc',
          hover: '#f1f5f9',
        },
        border: {
          DEFAULT: '#e2e8f0',
          strong: '#cbd5e1',
        },
        text: {
          primary: '#0f172a',
          secondary: '#475569',
          muted: '#94a3b8',
          inverse: '#ffffff',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        heading: ['Inter', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        'heading-xl': ['2.25rem', { lineHeight: '1.2', letterSpacing: '-0.02em' }],
        'heading-lg': ['1.875rem', { lineHeight: '1.2', letterSpacing: '-0.02em' }],
        'heading-md': ['1.5rem', { lineHeight: '1.3', letterSpacing: '-0.01em' }],
        'heading-sm': ['1.25rem', { lineHeight: '1.4' }],
        'body-lg': ['1.125rem', { lineHeight: '1.6' }],
        'body': ['1rem', { lineHeight: '1.6' }],
        'body-sm': ['0.875rem', { lineHeight: '1.5' }],
        'caption': ['0.75rem', { lineHeight: '1.5' }],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      boxShadow: {
        'card': '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
        'card-hover': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
        'elevated': '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
      },
      borderRadius: {
        'card': '12px',
        'button': '8px',
      },
      animation: {
        'fade-in': 'fadeIn 0.2s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-soft': 'pulseSoft 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
      },
    },
  },
  plugins: [],
}