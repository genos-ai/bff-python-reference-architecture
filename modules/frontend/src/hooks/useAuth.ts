import { useMutation, useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "@/lib/api";
import { ROUTES } from "@/lib/constants";
import { useAuthStore } from "@/stores/authStore";
import type { AuthResponse } from "@/types/auth";

export function useRequestMagicLink() {
  return useMutation({
    mutationFn: (email: string) =>
      apiFetch("/api/v1/auth/magic-link", {
        method: "POST",
        body: JSON.stringify({ email }),
      }),
  });
}

export function useVerifyToken() {
  const setTokens = useAuthStore((s) => s.setTokens);
  const setUser = useAuthStore((s) => s.setUser);
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (token: string) =>
      apiFetch<AuthResponse>("/api/v1/auth/verify", {
        method: "POST",
        body: JSON.stringify({ token }),
      }),
    onSuccess: (data) => {
      setTokens(data.access_token, data.sse_token);
      setUser(data.user);
      const needsOnboarding = !data.user.display_name;
      navigate(needsOnboarding ? ROUTES.SETTINGS : ROUTES.DASHBOARD);
    },
  });
}

export function useRefreshToken() {
  const setTokens = useAuthStore((s) => s.setTokens);
  const setUser = useAuthStore((s) => s.setUser);
  const clear = useAuthStore((s) => s.clear);

  return useQuery({
    queryKey: ["auth-refresh"],
    queryFn: async () => {
      try {
        const data = await apiFetch<AuthResponse>("/api/v1/auth/refresh", {
          method: "POST",
        });
        setTokens(data.access_token, data.sse_token);
        setUser(data.user);
        return data;
      } catch {
        clear();
        throw new Error("Refresh failed");
      }
    },
    refetchInterval: 25 * 60 * 1000, // 25 minutes
    enabled: useAuthStore.getState().isAuthenticated,
    retry: false,
  });
}

export function useLogout() {
  const clear = useAuthStore((s) => s.clear);
  const navigate = useNavigate();

  return useMutation({
    mutationFn: () =>
      apiFetch("/api/v1/auth/logout", { method: "POST" }),
    onSettled: () => {
      clear();
      navigate(ROUTES.LOGIN);
    },
  });
}
