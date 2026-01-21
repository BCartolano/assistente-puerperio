/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Cores conforme UX Expert
        'sus-blue': '#2563eb',      // Azul SUS (Público)
        'private-green': '#059669',  // Verde (Privado)
        'emergency-yellow': '#eab308', // Amarelo UPA
        'routine-gray': '#6b7280', // Cinza UBS
        'panic-red': '#dc2626',      // Vermelho Emergência
      },
    },
  },
  plugins: [],
}
