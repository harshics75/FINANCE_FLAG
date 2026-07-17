import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "/api/v1",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Automatic refresh-token retry on 401
let refreshing: Promise<string> | null = null;
api.interceptors.response.use(undefined, async (error) => {
  const original = error.config;
  if (error.response?.status === 401 && !original._retry) {
    const refresh = localStorage.getItem("refresh_token");
    if (!refresh) { window.location.href = "/login"; return Promise.reject(error); }
    original._retry = true;
    refreshing ??= api.post("/auth/refresh", { refresh_token: refresh }).then((r) => {
      localStorage.setItem("access_token", r.data.access_token);
      localStorage.setItem("refresh_token", r.data.refresh_token);
      return r.data.access_token as string;
    }).finally(() => { refreshing = null; });
    try {
      const token = await refreshing;
      original.headers.Authorization = `Bearer ${token}`;
      return api(original);
    } catch {
      localStorage.clear();
      window.location.href = "/login";
    }
  }
  return Promise.reject(error);
});

export default api;
