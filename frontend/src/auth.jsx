import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import * as api from "./api.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(!!api.getToken()); // sedang memverifikasi token tersimpan
  const [notice, setNotice] = useState("");

  const logout = useCallback((message = "") => {
    api.setToken(null);
    setUser(null);
    setNotice(message);
  }, []);

  useEffect(() => {
    api.setUnauthorizedHandler(() => logout("Sesi berakhir. Silakan masuk lagi."));
  }, [logout]);

  // Pulihkan sesi dari token yang tersimpan
  useEffect(() => {
    if (!api.getToken()) return;
    let alive = true;
    api
      .fetchMe()
      .then((u) => alive && setUser(u))
      .catch(() => {
        /* 401 sudah ditangani handler; error jaringan → tetap di halaman masuk */
      })
      .finally(() => alive && setChecking(false));
    return () => {
      alive = false;
    };
  }, []);

  const start = (session) => {
    api.setToken(session.access_token);
    setUser(session.user);
    setNotice("");
  };

  const value = useMemo(
    () => ({
      user,
      checking,
      notice,
      logout,
      login: async (email, password) => start(await api.login(email, password)),
      register: async (name, email, password) => start(await api.register(name, email, password)),
    }),
    [user, checking, notice, logout]
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
