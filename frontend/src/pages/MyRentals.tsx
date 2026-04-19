import React from "react";
import Box from "@mui/joy/Box";
import Chip from "@mui/joy/Chip";
import Sheet from "@mui/joy/Sheet";
import Table from "@mui/joy/Table";
import Typography from "@mui/joy/Typography";
import { apiFetch } from "../api/client";
import { useMe } from "../auth/useMe";
import AppShell from "../components/AppShell";

type HardwareItem = {
  id: number;
  name: string;
  brand: string;
  serialNumber: string | null;
  status: "Available" | "In Use" | "Repair" | "Unknown";
};

type HardwareListResponse = {
  items: HardwareItem[];
  page: number;
  limit: number;
  total: number;
  totalPages: number;
};

function toUiStatus(status: HardwareItem["status"]) {
  if (status === "In Use") return "Rented";
  if (status === "Repair") return "In Repair";
  if (status === "Unknown") return "Unknown";
  return "Available";
}

export default function MyRentalsPage() {
  const { state: meState } = useMe();
  const [rows, setRows] = React.useState<HardwareItem[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (meState.status !== "authed") {
      setLoading(meState.status === "loading");
      return;
    }

    const email = meState.me.email;
    const params = new URLSearchParams();
    params.set("assignedTo", email);
    params.set("status", "In Use");
    params.set("page", "1");
    params.set("limit", "20");

    let cancelled = false;
    setLoading(true);
    apiFetch<HardwareListResponse>(`/api/hardware?${params.toString()}`)
      .then((data) => {
        if (cancelled) return;
        setRows(data.items);
        setError(null);
      })
      .catch(() => {
        if (cancelled) return;
        setError("Could not load your rentals.");
      })
      .finally(() => {
        if (cancelled) return;
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [meState]);

  return (
    <AppShell title="My Rentals">
      <Sheet
        variant="outlined"
        sx={{ borderRadius: "md", overflow: "hidden", width: "100%", maxWidth: 790, borderColor: "#e9ebf0" }}
      >
        <Table
          size="sm"
          sx={{
            "--TableCell-paddingY": "4px",
            "--TableCell-paddingX": "8px",
            "& thead th": { fontSize: 10, fontWeight: 500, color: "#6b7280" },
            "& tbody td": { fontSize: 10, color: "#1f2937" },
          }}
        >
          <thead>
            <tr>
              <th>Device Name</th>
              <th>Brand</th>
              <th>Serial Number</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={5}>Loading...</td>
              </tr>
            ) : error ? (
              <tr>
                <td colSpan={5}>{error}</td>
              </tr>
            ) : rows.length === 0 ? (
              <tr>
                <td colSpan={5}>
                  <Typography level="body-sm" sx={{ color: "neutral.500", textAlign: "center", py: 0.75 }}>
                    {"You don't have any active rentals"}
                  </Typography>
                </td>
              </tr>
            ) : (
              rows.map((row) => {
                const uiStatus = toUiStatus(row.status);
                return (
                  <tr key={row.id}>
                    <td>{row.name}</td>
                    <td>{row.brand}</td>
                    <td>{row.serialNumber || ""}</td>
                    <td>
                      <Chip
                        size="sm"
                        sx={{
                          bgcolor: uiStatus === "In Repair" ? "#e11d48" : "#0b1220",
                          color: "white",
                          borderRadius: 999,
                          minHeight: 16,
                          fontSize: 8.5,
                        }}
                      >
                        {uiStatus}
                      </Chip>
                    </td>
                    <td>
                      <Box sx={{ fontSize: 8.6, color: "#9ca3af" }}>—</Box>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </Table>
      </Sheet>
    </AppShell>
  );
}
