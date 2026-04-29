import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "@/lib/api";
import { QUERY_KEYS, ROUTES } from "@/lib/constants";
import { useAuthStore } from "@/stores/authStore";
import { useUIStore } from "@/stores/uiStore";
import type { SettingsView } from "@/types/connection";
import { ErrorState, LoadingState } from "@/components/features/shared";

export default function Settings() {
  const navigate = useNavigate();
  const clear = useAuthStore((s) => s.clear);
  const setUser = useAuthStore((s) => s.setUser);
  const addToast = useUIStore((s) => s.addToast);
  const queryClient = useQueryClient();

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: [QUERY_KEYS.SETTINGS],
    queryFn: () => apiFetch<SettingsView>("/api/v1/views/settings"),
  });

  const [displayName, setDisplayName] = useState<string>("");
  const [initialized, setInitialized] = useState(false);

  if (data && !initialized) {
    setDisplayName(data.user.display_name ?? "");
    setInitialized(true);
  }

  const updateProfile = useMutation({
    mutationFn: (name: string) =>
      apiFetch<{ id: string; email: string; display_name: string | null }>(
        "/api/v1/users/me",
        {
          method: "PATCH",
          body: JSON.stringify({ display_name: name || null }),
        },
      ),
    onSuccess: (user) => {
      setUser({ id: user.id, email: user.email, display_name: user.display_name });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SETTINGS] });
      addToast("Profile updated", "success");
    },
  });

  const deleteAccount = useMutation({
    mutationFn: () => apiFetch("/api/v1/users/me", { method: "DELETE" }),
    onSuccess: () => {
      clear();
      navigate(ROUTES.LOGIN);
    },
  });

  if (isLoading) return <LoadingState />;
  if (isError)
    return <ErrorState message="Couldn't load settings." onRetry={refetch} />;
  if (!data) return null;

  const storagePct =
    data.storage_limit_bytes > 0
      ? (data.storage_used_bytes / data.storage_limit_bytes) * 100
      : 0;
  const storageMB = (data.storage_used_bytes / 1048576).toFixed(1);
  const limitMB = (data.storage_limit_bytes / 1048576).toFixed(0);

  return (
    <div className="max-w-2xl space-y-6">
      {/* Profile */}
      <section className="rounded-lg border border-border bg-card p-4 space-y-4">
        <h2 className="text-sm font-semibold text-foreground">Profile</h2>
        <div>
          <label className="text-xs text-muted-foreground">Email</label>
          <p className="text-sm text-foreground">{data.user.email}</p>
        </div>
        <div>
          <label className="text-xs text-muted-foreground">Display Name</label>
          <div className="mt-1 flex gap-2">
            <input
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="Your name"
              className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm"
            />
            <button
              onClick={() => updateProfile.mutate(displayName)}
              disabled={updateProfile.isPending}
              className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
            >
              Save
            </button>
          </div>
        </div>
      </section>

      {/* Storage */}
      <section className="rounded-lg border border-border bg-card p-4 space-y-2">
        <h2 className="text-sm font-semibold text-foreground">Storage</h2>
        <div className="h-2 rounded-full bg-muted overflow-hidden">
          <div
            className="h-full rounded-full bg-primary transition-all"
            style={{ width: `${Math.min(storagePct, 100)}%` }}
          />
        </div>
        <p className="text-xs text-muted-foreground">
          {storageMB}MB of {limitMB}MB used ({storagePct.toFixed(1)}%)
        </p>
      </section>

      {/* Danger zone */}
      <section className="rounded-lg border border-destructive/50 bg-card p-4 space-y-3">
        <h2 className="text-sm font-semibold text-destructive">Danger Zone</h2>
        <p className="text-sm text-muted-foreground">
          This will permanently delete all your data including trades, notes,
          and attachments.
        </p>
        <button
          onClick={() => {
            if (
              confirm(
                "Are you sure? This will permanently delete all your data.",
              )
            ) {
              deleteAccount.mutate();
            }
          }}
          disabled={deleteAccount.isPending}
          className="rounded-md bg-destructive px-4 py-2 text-sm font-medium text-destructive-foreground hover:bg-destructive/90 disabled:opacity-50"
        >
          Delete Account
        </button>
      </section>
    </div>
  );
}
