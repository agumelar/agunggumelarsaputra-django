/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './apps/**/templates/**/*.html',
    './apps/**/forms.py',
    './static/js/**/*.js',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#090d16',
        foreground: '#f3f4f6',
        surface: {
          DEFAULT: '#090d16',
          lowest: '#0d121e',
          low: '#111827',
          base: '#162032',
          high: '#1c293e',
          highest: '#23324d',
        },
        primary: {
          DEFAULT: '#38bdf8',
          container: 'rgba(56, 189, 248, 0.12)',
          'on-primary': '#082f49',
          'on-container': '#bae6fd',
        },
        secondary: {
          DEFAULT: '#2dd4bf',
          container: 'rgba(45, 212, 191, 0.12)',
          'on-secondary': '#042f2e',
          'on-container': '#99f6e4',
        },
        tertiary: {
          DEFAULT: '#fbbf24',
          container: 'rgba(251, 191, 36, 0.12)',
          'on-tertiary': '#451a03',
          'on-container': '#fde68a',
        },
        outline: {
          DEFAULT: 'rgba(255, 255, 255, 0.14)',
          variant: 'rgba(255, 255, 255, 0.08)',
        },
        success: '#34d399',
        warning: '#fbbf24',
        danger: '#f87171',
      },
      fontFamily: {
        display: ['Outfit', 'Inter', 'sans-serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      borderRadius: {
        xs: '4px',
        sm: '8px',
        md: '12px',
        lg: '16px',
        xl: '20px',
        '2xl': '24px',
        full: '9999px',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};
