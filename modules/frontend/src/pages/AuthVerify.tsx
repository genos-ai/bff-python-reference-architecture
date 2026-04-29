import { useEffect } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { useVerifyToken } from "@/hooks/useAuth";
import { ROUTES } from "@/lib/constants";
import { LoadingState } from "@/components/features/shared";

export default function AuthVerify() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const verify = useVerifyToken();

  useEffect(() => {
    if (token && !verify.isPending && !verify.isSuccess && !verify.isError) {
      verify.mutate(token);
    }
  }, [token]); // eslint-disable-line react-hooks/exhaustive-deps

  if (!token) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <p className="text-foreground">Invalid link.</p>
          <Link to={ROUTES.LOGIN} className="mt-2 text-sm text-primary hover:underline">
            Back to login
          </Link>
        </div>
      </div>
    );
  }

  if (verify.isError) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <p className="text-foreground">
            This link has expired or already been used.
          </p>
          <Link
            to={ROUTES.LOGIN}
            className="mt-2 inline-block text-sm text-primary hover:underline"
          >
            Request new link
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <LoadingState message="Signing you in..." />
    </div>
  );
}
