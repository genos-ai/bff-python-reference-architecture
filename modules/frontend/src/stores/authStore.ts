import { create } from "zustand";
import type { User } from "@/types/auth";

interface AuthState {
  accessToken: string | null;
  sseToken: string | null;
  user: User | null;
  isAuthenticated: boolean;
  setTokens: (access: string, sse: string) => void;
  setUser: (user: User) => void;
  clear: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  sseToken: null,
  user: null,
  isAuthenticated: false,

  setTokens: (access, sse) =>
    set({ accessToken: access, sseToken: sse, isAuthenticated: true }),

  setUser: (user) => set({ user }),

  clear: () =>
    set({
      accessToken: null,
      sseToken: null,
      user: null,
      isAuthenticated: false,
    }),
}));
