/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,ts}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef6fa',
          100: '#d6eaf3',
          200: '#acd4e7',
          500: '#1784b3',
          600: '#0b6b97',
          700: '#0a5a80',
          800: '#0b4a69',
          900: '#0c3d56',
        },
      },
      fontFamily: {
        sans: ['"Segoe UI"', 'Roboto', '"Helvetica Neue"', 'Arial', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
