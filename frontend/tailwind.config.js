/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        linkedin: {
          blue: '#0A66C2',
          'light-blue': '#378fe9',
          'dark-blue': '#004182',
          background: '#F3F2EF',
          'card-bg': '#FFFFFF',
          text: '#000000',
          'text-secondary': '#666666',
          success: '#057642',
          warning: '#F5C75D',
          border: '#E0DFDC',
        }
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', 'sans-serif'],
      }
    },
  },
  plugins: [],
}

