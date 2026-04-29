import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import { ROUTES } from "@/lib/constants";
import { Layout } from "@/components/Layout";
import Login from "@/pages/Login";
import AuthVerify from "@/pages/AuthVerify";
import Dashboard from "@/pages/Dashboard";
import PositionList from "@/pages/PositionList";
import PositionDetail from "@/pages/PositionDetail";
import Connections from "@/pages/Connections";
import Settings from "@/pages/Settings";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  if (!isAuthenticated) return <Navigate to={ROUTES.LOGIN} replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path={ROUTES.LOGIN} element={<Login />} />
        <Route path={ROUTES.AUTH_VERIFY} element={<AuthVerify />} />

        {/* Protected routes */}
        <Route
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route path={ROUTES.DASHBOARD} element={<Dashboard />} />
          <Route path={ROUTES.POSITIONS} element={<PositionList />} />
          <Route path={ROUTES.POSITION_DETAIL} element={<PositionDetail />} />
          <Route path={ROUTES.CONNECTIONS} element={<Connections />} />
          <Route path={ROUTES.SETTINGS} element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
