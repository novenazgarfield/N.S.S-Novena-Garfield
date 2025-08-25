import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 52333,
    allowedHosts: true
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        dashboard: resolve(__dirname, 'nexus-dashboard-restored.html'),
        modular: resolve(__dirname, 'nexus-dashboard-modular.html'),
        optimized: resolve(__dirname, 'nexus-dashboard-optimized.html')
      },
      output: {
        manualChunks: {
          'themes': ['./assets/js/themes.js'],
          'navigation': ['./assets/js/navigation.js'],
          'rag': ['./assets/js/rag.js']
        }
      }
    },
    cssCodeSplit: true,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    }
  },
  css: {
    devSourcemap: true,
    preprocessorOptions: {
      css: {
        charset: false
      }
    }
  },
  optimizeDeps: {
    include: ['./assets/js/themes.js', './assets/js/navigation.js', './assets/js/rag.js']
  }
})
