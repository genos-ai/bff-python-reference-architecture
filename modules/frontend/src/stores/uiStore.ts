import { create } from "zustand";

interface Toast {
  id: string;
  message: string;
  type: "success" | "error" | "info";
}

interface UIState {
  toasts: Toast[];
  sidebarOpen: boolean;
  addToast: (message: string, type?: Toast["type"]) => void;
  removeToast: (id: string) => void;
  toggleSidebar: () => void;
}

let toastCounter = 0;

export const useUIStore = create<UIState>((set) => ({
  toasts: [],
  sidebarOpen: false,

  addToast: (message, type = "info") => {
    const id = String(++toastCounter);
    set((state) => ({
      toasts: [...state.toasts, { id, message, type }],
    }));
    setTimeout(() => {
      set((state) => ({
        toasts: state.toasts.filter((t) => t.id !== id),
      }));
    }, 5000);
  },

  removeToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    })),

  toggleSidebar: () =>
    set((state) => ({ sidebarOpen: !state.sidebarOpen })),
}));
