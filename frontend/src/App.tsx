import React from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import LoginPage from "./pages/Login";
import DashboardPage from "./pages/Dashboard";
import MyRentalsPage from "./pages/MyRentals";
import AdminPanelPage from "./pages/AdminPanel";
import { useMe } from "./auth/useMe";

export default function App() {
  const { state: meState, setAuthed } = useMe();
  const location = useLocation();
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
                <AdminPanelPage />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
        </Routes>
      </motion.div>
    </AnimatePresence>
  );
}

