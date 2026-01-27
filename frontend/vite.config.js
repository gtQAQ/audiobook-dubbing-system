import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/token': 'http://127.0.0.1:8000',
      '/register': 'http://127.0.0.1:8000',
      '/users': 'http://127.0.0.1:8000',
      '/audio': 'http://127.0.0.1:8000',
      '/voice': 'http://127.0.0.1:8000',
      '/output': 'http://127.0.0.1:8000',
    }
  }
})
