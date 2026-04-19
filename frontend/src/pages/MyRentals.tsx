import React from "react";
import Box from "@mui/joy/Box";
import Button from "@mui/joy/Button";
import Chip from "@mui/joy/Chip";
import Sheet from "@mui/joy/Sheet";
import Table from "@mui/joy/Table";
import Typography from "@mui/joy/Typography";
import { apiFetch, type ApiError } from "../api/client";
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
  const [actionError, setActionError] = React.useState<string | null>(null);
  const [pendingRowId, setPendingRowId] = React.useState<number | null>(null);

  const reload = React.useCallback(() => {
    if (meState.status !== "authed") {
      return Promise.resolve();
    }
    const email = meState.me.email;
    const params = new URLSearchParams();
    params.set("assignedTo", email);
    params.set("status", "In Use");
    params.set("page", "1");
    params.set("limit", "20");
    return apiFetch<HardwareListResponse>(`/api/hardware?${params.toString()}`).then(
      (data) => {
        setRows(data.items);
        setError(null);
      },
    );
  }, [meState]);

  React.useEffect(() => {
    if (meState.status !== "authed") {
      setLoading(meState.status === "loading");
      return;
    }

    let cancelled = false;
    setLoading(true);
    reload()
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
  }, [meState, reload]);

  function returnDevice(row: HardwareItem) {
    setActionError(null);
    setPendingRowId(row.id);
    apiFetch<HardwareItem>(`/api/hardware/${row.id}/return`, { method: "POST" })
      .then(() => reload())
      .catch((err) => {
        const apiErr = err as ApiError;
        const code =
          apiErr?.data && typeof apiErr.data === "object" && apiErr.data !== null
            ? (apiErr.data as { error?: string }).error
            : undefined;
        if (code === "forbidden_return") {
          setActionError("You can only return your own rentals.");
        } else if (code === "cannot_return") {
          setActionError("This device cannot be returned.");
        } else {
          setActionError("Return failed. Try again.");
        }
      })
      .finally(() => setPendingRowId(null));
  }

  return (
    <AppShell title="My Rentals">
      {actionError ? (
        <Box sx={{ mb: 0.75, fontSize: 10, color: "#b91c1c" }}>{actionError}</Box>
      ) : null}
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
                const busy = pendingRowId === row.id;
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
                      <Button
                        size="sm"
                        loading={busy}
                        disabled={busy}
                        onClick={() => returnDevice(row)}
                        sx={{
                          minHeight: 18,
                          px: 1,
                          borderRadius: "sm",
                          bgcolor: "#374151",
                          color: "white",
                          fontSize: 8.6,
                          ":hover": { bgcolor: "#374151" },
                        }}
                      >
                        Return
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
