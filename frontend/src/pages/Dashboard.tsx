import React from "react";
import Box from "@mui/joy/Box";
import Button from "@mui/joy/Button";
import Chip from "@mui/joy/Chip";
import Input from "@mui/joy/Input";
import Sheet from "@mui/joy/Sheet";
import Table from "@mui/joy/Table";
import AppShell from "../components/AppShell";
import { apiFetch } from "../api/client";

type HardwareItem = {
  id: number;
  name: string;
  brand: string;
  purchaseDate: string | null;
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
  return status;
}

export default function DashboardPage() {
  const [rows, setRows] = React.useState<HardwareItem[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let cancelled = false;

    apiFetch<HardwareListResponse>("/api/hardware?page=1&limit=20")
      .then((data) => {
        if (cancelled) return;
        setRows(data.items);
        setError(null);
      })
      .catch(() => {
        if (cancelled) return;
        setError("Could not load hardware list.");
      })
      .finally(() => {
        if (cancelled) return;
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <AppShell title="Hardware List">
      <Box sx={{ width: "100%", maxWidth: 790 }}>
        <Input
          size="sm"
          placeholder="Ask AI..."
          sx={{ mb: 0.65, height: 24, fontSize: 10 }}
          endDecorator={<Box sx={{ color: "#8b5cf6", fontSize: 10 }}>✧</Box>}
        />
      </Box>
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
              <th>Date Added</th>
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
                <td colSpan={5}>No hardware found.</td>
              </tr>
            ) : (
              rows.map((row) => {
                const uiStatus = toUiStatus(row.status);
                const canRent = row.status === "Available";
                return (
                  <tr key={row.id}>
                    <td>{row.name}</td>
                    <td>{row.brand}</td>
                    <td>{row.purchaseDate || "-"}</td>
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
                      <Button
                        size="sm"
                        disabled={!canRent}
                        sx={{
                          minHeight: 18,
                          px: 1,
                          borderRadius: "sm",
                          bgcolor: "#0b1220",
                          color: "white",
                          fontSize: 8.6,
                          ":hover": { bgcolor: "#0b1220" },
                        }}
                      >
                        Rent
                      </Button>
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

