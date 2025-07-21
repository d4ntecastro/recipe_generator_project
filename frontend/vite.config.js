    import { defineConfig } from 'vite'
    import react from '@vitejs/plugin-react'

    // https://vitejs.dev/config/
    export default defineConfig({
      plugins: [react()],
      base: '/static/', // <--- ADD THIS LINE! This tells Vite to prepend /static/ to all asset paths.
      build: {
        outDir: 'dist', // Ensure this is 'dist'
      }
    })
    