import React from "react";
import Box from "@mui/joy/Box";
import Button from "@mui/joy/Button";
import Chip from "@mui/joy/Chip";
import Input from "@mui/joy/Input";
import Sheet from "@mui/joy/Sheet";
import Table from "@mui/joy/Table";
import Typography from "@mui/joy/Typography";
import AppShell from "../components/AppShell";
import { apiFetch, type ApiError } from "../api/client";
import { useMe } from "../auth/useMe";

type HardwareItem = {
  id: number;
  name: string;
  brand: string;
  purchaseDate: string | null;
  status: "Available" | "In Use" | "Repair" | "Unknown";
  assignedTo: string | null;
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

const PAGE_SIZE = 20;

export default function DashboardPage() {
  const { state: meState } = useMe();
  const [rows, setRows] = React.useState<HardwareItem[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [actionError, setActionError] = React.useState<string | null>(null);
  const [pendingRowId, setPendingRowId] = React.useState<number | null>(null);
  const [page, setPage] = React.useState(1);
  const [totalPages, setTotalPages] = React.useState(1);

  const loadList = React.useCallback(() => {
    const params = new URLSearchParams();
    params.set("page", String(page));
    params.set("limit", String(PAGE_SIZE));
    return apiFetch<HardwareListResponse>(`/api/hardware?${params.toString()}`)
      .then((data) => {
        const tp = Math.max(1, data.totalPages);
        setTotalPages(tp);
        setRows(data.items);
        setError(null);
        if (page > tp) {
          setPage(tp);
        }
      })
      .catch(() => {
        setError("Could not load hardware list.");
      });
  }, [page]);

  React.useEffect(() => {
    let cancelled = false;
    setLoading(true);
    loadList().finally(() => {
      if (!cancelled) setLoading(false);
    });
    return () => {
      cancelled = true;
    };
  }, [loadList]);

  const myEmail =
    meState.status === "authed" ? meState.me.email.trim().toLowerCase() : "";

  function runRentReturn(row: HardwareItem, action: "rent" | "return") {
    setActionError(null);
    setPendingRowId(row.id);
    const path =
      action === "rent"
        ? `/api/hardware/${row.id}/rent`
        : `/api/hardware/${row.id}/return`;
    apiFetch<HardwareItem>(path, { method: "POST" })
      .then(() => loadList())
      .catch((err) => {
        const apiErr = err as ApiError;
        const code =
          apiErr?.data && typeof apiErr.data === "object" && apiErr.data !== null
            ? (apiErr.data as { error?: string }).error
            : undefined;
        if (code === "cannot_rent") {
          setActionError("This device is not available to rent.");
        } else if (code === "cannot_return") {
          setActionError("This device cannot be returned.");
        } else if (code === "forbidden_return") {
          setActionError("You can only return your own rentals.");
        } else {
          setActionError("Action failed. Try again.");
        }
      })
      .finally(() => setPendingRowId(null));
  }

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
                const assigned = (row.assignedTo || "").trim().toLowerCase();
                const canReturn =
                  row.status === "In Use" && myEmail.length > 0 && assigned === myEmail;
                const busy = pendingRowId === row.id;
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
                      {canReturn ? (
                        <Button
                          size="sm"
                          loading={busy}
                          disabled={busy}
                          onClick={() => runRentReturn(row, "return")}
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
                      ) : (
                        <Button
                          size="sm"
                          loading={busy && canRent}
                          disabled={!canRent || busy}
                          onClick={() => canRent && runRentReturn(row, "rent")}
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
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </Table>
      </Sheet>
      <Box
        sx={{
          width: "100%",
          maxWidth: 790,
          mt: 0.7,
          display: "flex",
          justifyContent: "flex-end",
          gap: 0.8,
        }}
      >
        <Button
          size="sm"
          variant="outlined"
          color="neutral"
          disabled={page <= 1 || loading}
          onClick={() => setPage((p) => Math.max(1, p - 1))}
        >
          Prev
        </Button>
        <Typography level="body-sm" sx={{ alignSelf: "center", color: "#6b7280" }}>
          Page {page} of {totalPages}
        </Typography>
        <Button
          size="sm"
          variant="outlined"
          color="neutral"
          disabled={page >= totalPages || loading}
          onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
        >
          Next
        </Button>
      </Box>
    </AppShell>
  );
}

