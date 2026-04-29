import { useEffect, useRef } from "react";
import { Link, Outlet, useLocation } from "react-router-dom";
import { LayoutDashboard, LineChart, Plug, Settings, LogOut } from "lucide-react";
import { cn } from "@/lib/cn";
import { ROUTES } from "@/lib/constants";
import { connectSSE } from "@/lib/sse";
import { useLogout } from "@/hooks/useAuth";
import { useAuthStore } from "@/stores/authStore";
import { useUIStore } from "@/stores/uiStore";

const NAV_ITEMS = [
  { label: "Dashboard", href: ROUTES.DASHBOARD, icon: LayoutDashboard },
  { label: "Positions", href: ROUTES.POSITIONS, icon: LineChart },
  { label: "Connections", href: ROUTES.CONNECTIONS, icon: Plug },
  { label: "Settings", href: ROUTES.SETTINGS, icon: Settings },
];

export function Layout() {
  const location = useLocation();
  const user = useAuthStore((s) => s.user);
  const sseToken = useAuthStore((s) => s.sseToken);
  const logout = useLogout();
  const toasts = useUIStore((s) => s.toasts);
  const removeToast = useUIStore((s) => s.removeToast);
  const sseRef = useRef<EventSource | null>(null);

  // Connect SSE when authenticated
  useEffect(() => {
    if (sseToken && !sseRef.current) {
      sseRef.current = connectSSE(sseToken);
    }
    return () => {
      sseRef.current?.close();
      sseRef.current = null;
    };
  }, [sseToken]);

  return (
    <div className="min-h-screen bg-background">
      {/* Top nav */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto flex h-14 items-center justify-between px-4">
          <div className="flex items-center gap-6">
            <Link to="/" className="text-lg font-bold text-foreground">
              BFF Web
            </Link>
            <nav className="hidden md:flex items-center gap-1">
              {NAV_ITEMS.map((item) => (
                <Link
                  key={item.href}
                  to={item.href}
                  className={cn(
                    "flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                    location.pathname === item.href
                      ? "bg-accent text-accent-foreground"
                      : "text-muted-foreground hover:text-foreground hover:bg-accent/50",
                  )}
                >
                  <item.icon className="h-4 w-4" />
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">
              {user?.display_name ?? user?.email}
            </span>
            <button
              onClick={() => logout.mutate()}
              className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="container mx-auto px-4 py-6">
        <Outlet />
      </main>

      {/* Toast notifications */}
      <div className="fixed bottom-4 right-4 flex flex-col gap-2 z-50">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            onClick={() => removeToast(toast.id)}
            className={cn(
              "rounded-lg px-4 py-3 text-sm font-medium shadow-lg cursor-pointer animate-in slide-in-from-right",
              toast.type === "success" && "bg-green-600 text-white",
              toast.type === "error" && "bg-red-600 text-white",
              toast.type === "info" && "bg-card text-foreground border border-border",
            )}
          >
            {toast.message}
          </div>
        ))}
      </div>
    </div>
  );
}
