import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRequestMagicLink } from "@/hooks/useAuth";
import { apiFetch } from "@/lib/api";
import { ROUTES } from "@/lib/constants";
import { useAuthStore } from "@/stores/authStore";
import type { AuthResponse } from "@/types/auth";

const schema = z.object({
  email: z.string().email("Enter a valid email address"),
});

type FormData = z.infer<typeof schema>;

export default function Login() {
  const [sent, setSent] = useState(false);
  const [devLoading, setDevLoading] = useState(false);
  const mutation = useRequestMagicLink();
  const navigate = useNavigate();
  const setTokens = useAuthStore((s) => s.setTokens);
  const setUser = useAuthStore((s) => s.setUser);
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  const emailValue = watch("email");

  const onSubmit = (data: FormData) => {
    mutation.mutate(data.email, {
      onSuccess: () => setSent(true),
    });
  };

  const devLogin = async () => {
    const email = emailValue || "dev@example.com";
    setDevLoading(true);
    try {
      const data = await apiFetch<AuthResponse>("/api/v1/auth/dev-login", {
        method: "POST",
        body: JSON.stringify({ email }),
      });
      setTokens(data.access_token, data.sse_token);
      setUser(data.user);
      navigate(data.user.display_name ? ROUTES.DASHBOARD : ROUTES.SETTINGS);
    } catch {
      setDevLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="w-full max-w-sm space-y-6 p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-foreground">BFF Web</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Enter your email to receive a login link.
          </p>
        </div>

        {sent ? (
          <div className="rounded-lg border border-border bg-card p-4 text-center">
            <p className="text-sm text-foreground">
              Check your email for the login link. It expires in 30 minutes.
            </p>
            <button
              onClick={() => setSent(false)}
              className="mt-3 text-sm text-primary hover:underline"
            >
              Send again
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <input
                {...register("email")}
                type="email"
                placeholder="trader@example.com"
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                disabled={mutation.isPending || devLoading}
              />
              {errors.email && (
                <p className="mt-1 text-xs text-destructive">
                  {errors.email.message}
                </p>
              )}
            </div>
            <button
              type="submit"
              disabled={mutation.isPending || devLoading}
              className="w-full rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
            >
              {mutation.isPending ? "Sending..." : "Send magic link"}
            </button>
            <button
              type="button"
              onClick={devLogin}
              disabled={devLoading}
              className="w-full rounded-md border border-border bg-card px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent disabled:opacity-50"
            >
              {devLoading ? "Logging in..." : "Dev Login (skip email)"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
