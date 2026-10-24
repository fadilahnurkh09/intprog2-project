import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["icons/apple-touch-icon.png", "favicon.svg"],
      manifest: {
        name: "FrameFit — Kacamata yang Pas untuk Wajahmu",
        short_name: "FrameFit",
        description: "Analisis bentuk wajah, rekomendasi kacamata, dan Virtual Try-On.",
        lang: "id",
        start_url: "/",
        scope: "/",
        display: "standalone",
        orientation: "portrait",
        theme_color: "#221d19",
        background_color: "#f6f1e9",
        categories: ["lifestyle", "shopping"],
        icons: [
          { src: "icons/icon-192.png", sizes: "192x192", type: "image/png" },
          { src: "icons/icon-512.png", sizes: "512x512", type: "image/png" },
          { src: "icons/maskable-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
        ],
      },
      workbox: {
        globPatterns: ["**/*.{js,css,html,svg,png,woff2}"],
        // Jangan tampilkan index.html untuk path API jika backend ada di domain yang sama
        navigateFallback: "/index.html",
        navigateFallbackDenylist: [/^\/(auth|predict|analyze|try-on|recommendations|assets|docs|openapi\.json)/],
        maximumFileSizeToCacheInBytes: 3 * 1024 * 1024,
        runtimeCaching: [
          {
            // CSS Google Fonts
            urlPattern: ({ url }) => url.origin === "https://fonts.googleapis.com",
            handler: "StaleWhileRevalidate",
            options: { cacheName: "gfonts-css" },
          },
          {
            // File font
            urlPattern: ({ url }) => url.origin === "https://fonts.gstatic.com",
            handler: "CacheFirst",
            options: {
              cacheName: "gfonts-files",
              expiration: { maxEntries: 20, maxAgeSeconds: 60 * 60 * 24 * 365 },
              cacheableResponse: { statuses: [0, 200] },
            },
          },
          {
            // Wasm + model MediaPipe (mode manual) — diunduh sekali, lalu dari cache
            urlPattern: ({ url }) =>
              url.hostname === "cdn.jsdelivr.net" || url.hostname === "storage.googleapis.com",
            handler: "CacheFirst",
            options: {
              cacheName: "mediapipe",
              expiration: { maxEntries: 10, maxAgeSeconds: 60 * 60 * 24 * 90 },
              cacheableResponse: { statuses: [0, 200] },
            },
          },
        ],
        // Panggilan API (login, analisis, try-on) sengaja TIDAK di-cache.
      },
    }),
  ],
  server: { port: 5173 },
});
