import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import LoginPage from "./pages/Login";
import DashboardPage from "./pages/Dashboard";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
    </Routes>
  );
}

