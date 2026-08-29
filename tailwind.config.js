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
        background: 'var(--md-sys-color-surface)',
        foreground: 'var(--foreground)',
        muted: 'var(--muted-foreground)',
        surface: {
          DEFAULT: 'var(--md-sys-color-surface)',
          lowest: 'var(--md-sys-color-surface-container-lowest)',
          low: 'var(--md-sys-color-surface-container-low)',
          base: 'var(--md-sys-color-surface-container)',
          high: 'var(--md-sys-color-surface-container-high)',
          highest: 'var(--md-sys-color-surface-container-highest)',
        },
        primary: {
          DEFAULT: 'var(--md-sys-color-primary)',
          container: 'var(--md-sys-color-primary-container)',
          'on-primary': 'var(--md-sys-color-on-primary)',
          'on-container': 'var(--md-sys-color-on-primary-container)',
        },
        secondary: {
          DEFAULT: 'var(--md-sys-color-secondary)',
          container: 'var(--md-sys-color-secondary-container)',
          'on-secondary': 'var(--md-sys-color-on-secondary)',
          'on-container': 'var(--md-sys-color-on-secondary-container)',
        },
        tertiary: {
          DEFAULT: 'var(--md-sys-color-tertiary)',
          container: 'var(--md-sys-color-tertiary-container)',
          'on-tertiary': 'var(--md-sys-color-on-tertiary)',
          'on-container': 'var(--md-sys-color-on-tertiary-container)',
        },
        outline: {
          DEFAULT: 'var(--md-sys-color-outline)',
          variant: 'var(--md-sys-color-outline-variant)',
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
