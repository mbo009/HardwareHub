import React from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import LoginPage from "./pages/Login";
import DashboardPage from "./pages/Dashboard";
import MyRentalsPage from "./pages/MyRentals";
import AdminPanelPage from "./pages/AdminPanel";
import { useMe, type Me } from "./auth/useMe";
import ForcePasswordChangeModal from "./components/auth/ForcePasswordChangeModal";
import FloatingAssistantChat from "./components/FloatingAssistantChat";
import { apiFetch, type ApiError } from "./api/client";

export default function App() {
  const { state: meState, setAuthed } = useMe();
  const location = useLocation();
  const [isChangingPassword, setIsChangingPassword] = React.useState(false);
  const [changePasswordError, setChangePasswordError] = React.useState<
    string | null
  >(null);
  const isAppTabRoute =
    location.pathname === "/dashboard" ||
    location.pathname === "/my-rentals" ||
    location.pathname === "/admin-panel";

  if (meState.status === "loading") {
    return null;
  }

  return (
    <AnimatePresence mode="wait" initial={false}>
      <motion.div
        key={location.pathname}
        initial={
          isAppTabRoute
            ? { opacity: 1, filter: "blur(0px)", y: 0 }
            : { opacity: 0, filter: "blur(10px)", y: 4 }
        }
        animate={{ opacity: 1, filter: "blur(0px)", y: 0 }}
        exit={
          isAppTabRoute
            ? { opacity: 1, filter: "blur(0px)", y: 0 }
            : { opacity: 0, filter: "blur(10px)", y: -4 }
        }
        transition={
          isAppTabRoute
            ? { duration: 0 }
            : { duration: 0.34, ease: [0.22, 1, 0.36, 1] }
        }
      >
        <Routes location={location}>
          <Route
            path="/"
            element={
              meState.status === "authed" ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/login"
            element={<LoginPage onLoginSuccess={setAuthed} />}
          />
          <Route
            path="/dashboard"
            element={
              meState.status === "authed" ? (
                <DashboardPage />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/my-rentals"
            element={
              meState.status === "authed" ? (
                <MyRentalsPage />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/admin-panel"
            element={
              meState.status === "authed" ? (
                meState.me.role === "admin" ? (
                  <AdminPanelPage />
                ) : (
                  <Navigate to="/dashboard" replace />
                )
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
        </Routes>
        <FloatingAssistantChat
          email={meState.status === "authed" ? meState.me.email : null}
          role={meState.status === "authed" ? meState.me.role : null}
        />
        <ForcePasswordChangeModal
          open={
            meState.status === "authed" &&
            meState.me.mustChangePassword &&
            location.pathname !== "/login"
          }
          isSubmitting={isChangingPassword}
          error={changePasswordError}
          onSubmit={(newPassword) => {
            setIsChangingPassword(true);
            setChangePasswordError(null);
            apiFetch<Me>("/api/auth/change-password", {
              method: "POST",
              body: JSON.stringify({ newPassword }),
            })
              .then((me) => {
                setAuthed(me);
              })
              .catch((error) => {
                const err = error as ApiError;
                const data = err?.data as
                  | { error?: string; details?: string[] }
                  | undefined;
                if (data?.error === "invalid_password") {
                  setChangePasswordError(
                    "Password must include uppercase, digit and special character.",
                  );
                } else if (err?.status === 401) {
                  setChangePasswordError("Session expired. Please log in again.");
                } else {
                  setChangePasswordError("Could not change password. Try again.");
                }
              })
              .finally(() => {
                setIsChangingPassword(false);
              });
          }}
        />
      </motion.div>
    </AnimatePresence>
  );
}

