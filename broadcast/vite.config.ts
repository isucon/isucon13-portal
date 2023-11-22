import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';
import Pages from 'vite-plugin-pages';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), Pages({})],
  base: '/broadcast',
  server: {
    port: 5000,
    proxy: {
      '/contest/': {
        target: 'https://portal.xiii.isucon.dev/',
        changeOrigin: true,
      },
    },
  },
  resolve: {
    alias: [
      {
        find: '~/',
        replacement: '/src/',
      },
    ],
  },
});
