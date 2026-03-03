/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        surface: '#0a0a0f',
        panel: '#12121a',
        border: '#1e1e2e',
        accent: '#6366f1',
        'accent-dim': '#4f46e5',
        muted: '#64748b',
        converge: '#22c55e',
        diverge: '#ef4444',
        retreat: '#eab308',
      },
    },
  },
  plugins: [],
}
