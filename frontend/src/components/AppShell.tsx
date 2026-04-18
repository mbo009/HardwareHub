import React from "react";
import Box from "@mui/joy/Box";
import Button from "@mui/joy/Button";
import Divider from "@mui/joy/Divider";
import List from "@mui/joy/List";
import ListItem from "@mui/joy/ListItem";
import ListItemButton from "@mui/joy/ListItemButton";
import Sheet from "@mui/joy/Sheet";
import Typography from "@mui/joy/Typography";
import { NavLink, useLocation } from "react-router-dom";
import { apiFetch } from "../api/client";
import PackageIcon from "./PackageIcon";

type AppShellProps = {
  title: string;
  children: React.ReactNode;
};

const navItems = [
  { to: "/dashboard", label: "Hardware List", icon: "≡" },
  { to: "/my-rentals", label: "My Rentals", icon: "◌" },
  { to: "/admin-panel", label: "Admin Panel", icon: "✥" },
];

export default function AppShell({ title, children }: AppShellProps) {
  const location = useLocation();

  const onLogout = async () => {
    try {
      await apiFetch("/api/auth/logout", { method: "POST" });
    } finally {
      window.location.assign("/login");
    }
  };

  return (
    <Box sx={{ minHeight: "100vh", display: "flex", bgcolor: "#f6f7fb" }}>
      <Sheet
        variant="outlined"
        sx={{
          width: 154,
          borderTop: 0,
          borderBottom: 0,
          borderLeft: 0,
          borderRadius: 0,
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          py: 0.6,
          px: 0,
          bgcolor: "background.surface",
        }}
      >
        <Box>
          <Box sx={{ px: 1, py: 0.9, display: "flex", alignItems: "center", gap: 0.5 }}>
            <Box
              sx={{
                width: 14,
                height: 14,
                borderRadius: 4,
                bgcolor: "neutral.softBg",
                display: "grid",
                placeItems: "center",
                fontSize: 9,
                color: "neutral.700",
              }}
            >
              <PackageIcon size={10} color="currentColor" strokeWidth={1.9} />
            </Box>
            <Typography sx={{ fontSize: 10, fontWeight: 500, lineHeight: 1.1 }}>
              Hardware Manager
            </Typography>
          </Box>
          <Divider sx={{ mx: 0.7 }} />
          <List size="sm" sx={{ gap: 0.25, px: 0.85, pt: 0.75 }}>
            {navItems.map((item) => {
              const selected = location.pathname === item.to;
              return (
                <ListItem key={item.to}>
                  <ListItemButton
                    component={NavLink}
                    to={item.to}
                    selected={selected}
                    sx={{
                      borderRadius: "md",
                      fontWeight: 500,
                      fontSize: 10,
                      minHeight: 26,
                      px: 0.75,
                      gap: 0.6,
                      color: "#374151",
                      "&.active, &[aria-selected='true']": {
                        bgcolor: "#eef0f5",
                      },
                    }}
                  >
                    <Box sx={{ width: 9, textAlign: "center", color: "#9ca3af" }}>{item.icon}</Box>
                    {item.label}
                  </ListItemButton>
                </ListItem>
              );
            })}
          </List>
        </Box>

        <Box sx={{ p: 0.65 }}>
          <Divider sx={{ mb: 0.55, mx: 0.1 }} />
          <Button
            variant="plain"
            color="danger"
            size="sm"
            onClick={onLogout}
            sx={{ justifyContent: "flex-start", width: "100%", fontSize: 10, minHeight: 22 }}
          >
            Logout
          </Button>
        </Box>
      </Sheet>

      <Box sx={{ flex: 1, px: 2.2, py: 1.6 }}>
        <Box sx={{ width: "100%", maxWidth: 860, mx: "auto" }}>
          <Typography sx={{ mb: 1, fontSize: 18, fontWeight: 600, lineHeight: 1.2, color: "#111827" }}>
            {title}
          </Typography>
          {children}
        </Box>
      </Box>
    </Box>
  );
}

