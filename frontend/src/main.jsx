import React from "react";
import { createRoot } from "react-dom/client";
import { registerSW } from "virtual:pwa-register";
import App from "./App.jsx";
import { AuthProvider } from "./auth.jsx";
import "./styles.css";

// Service worker (PWA): aplikasi bisa dipasang dan memuat cepat dari cache.
// Versi baru otomatis aktif saat aplikasi dibuka kembali.
registerSW({ immediate: true });

createRoot(document.getElementById("root")).render(
  <AuthProvider>
    <App />
  </AuthProvider>
);
