import React from "react";
import Box from "@mui/joy/Box";
import Button from "@mui/joy/Button";
import Chip from "@mui/joy/Chip";
import Sheet from "@mui/joy/Sheet";
import Table from "@mui/joy/Table";
import Typography from "@mui/joy/Typography";
import AdminFilters from "../components/admin/AdminFilters";
import AppShell from "../components/AppShell";
import { apiFetch, type ApiError } from "../api/client";
import { useMe } from "../auth/useMe";
import { buildHardwareListSearchParams } from "../hardware/hardwareListQuery";

type HardwareItem = {
  id: number;
  name: string;
  brand: string;
  serialNumber: string | null;
  status: "Available" | "In Use" | "Repair" | "Unknown";
  preArrival?: boolean;
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

function isOrderedState(row: HardwareItem) {
  return Boolean(
    row.preArrival && (row.status === "Available" || row.status === "Unknown"),
  );
}

const PAGE_SIZE = 20;

export default function MyRentalsPage() {
  const { state: meState } = useMe();
  const [rows, setRows] = React.useState<HardwareItem[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [actionError, setActionError] = React.useState<string | null>(null);
  const [pendingRowId, setPendingRowId] = React.useState<number | null>(null);
  const [page, setPage] = React.useState(1);
  const [totalPages, setTotalPages] = React.useState(1);
  const [statusFilter, setStatusFilter] = React.useState("Rented");
  const [brandFilter, setBrandFilter] = React.useState("");
  const [debouncedBrandFilter, setDebouncedBrandFilter] = React.useState("");
  const [dateFromFilter, setDateFromFilter] = React.useState("");
  const [dateToFilter, setDateToFilter] = React.useState("");

  React.useEffect(() => {
    const t = window.setTimeout(() => {
      setDebouncedBrandFilter(brandFilter.trim());
      setPage(1);
    }, 400);
    return () => window.clearTimeout(t);
  }, [brandFilter]);

  const loadList = React.useCallback(() => {
    if (meState.status !== "authed") {
      return Promise.resolve();
    }
    const email = meState.me.email;
    const params = buildHardwareListSearchParams({
      assignedToEmail: email,
      statusFilter,
      brandFilter: debouncedBrandFilter,
      dateFrom: dateFromFilter,
      dateTo: dateToFilter,
      sortBy: "name",
      sortOrder: "asc",
      page,
      limit: PAGE_SIZE,
    });
    return apiFetch<HardwareListResponse>(`/api/hardware?${params.toString()}`).then(
      (data) => {
        const tp = Math.max(1, data.totalPages);
        setTotalPages(tp);
        setRows(data.items);
        setError(null);
        if (page > tp) {
          setPage(tp);
        }
      },
    );
  }, [
    meState,
    page,
    statusFilter,
    debouncedBrandFilter,
    dateFromFilter,
    dateToFilter,
  ]);

  React.useEffect(() => {
    if (meState.status !== "authed") {
      setLoading(meState.status === "loading");
      return;
    }

    let cancelled = false;
    setLoading(true);
    loadList()
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
  }, [meState, loadList]);

  const resetFilters = React.useCallback(() => {
    setStatusFilter("Rented");
    setBrandFilter("");
    setDebouncedBrandFilter("");
    setDateFromFilter("");
    setDateToFilter("");
    setPage(1);
  }, []);

  const isDefaultRentedView =
    statusFilter === "Rented" &&
    !debouncedBrandFilter &&
    !dateFromFilter &&
    !dateToFilter;

  function returnDevice(row: HardwareItem) {
    setActionError(null);
    setPendingRowId(row.id);
    apiFetch<HardwareItem>(`/api/hardware/${row.id}/return`, { method: "POST" })
      .then(() => loadList())
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
      <AdminFilters
        statusFilter={statusFilter}
        setStatusFilter={setStatusFilter}
        brandFilter={brandFilter}
        setBrandFilter={setBrandFilter}
        dateFromFilter={dateFromFilter}
        setDateFromFilter={setDateFromFilter}
        dateToFilter={dateToFilter}
        setDateToFilter={setDateToFilter}
        onReset={resetFilters}
        onFilterChangeResetPage={() => setPage(1)}
      />
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
                    {isDefaultRentedView
                      ? "You don't have any active rentals"
                      : "No matching rentals."}
                  </Typography>
                </td>
              </tr>
            ) : (
              rows.map((row) => {
                const ordered = isOrderedState(row);
                const chipLabel = ordered ? "Ordered" : toUiStatus(row.status);
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
                          bgcolor: ordered
                            ? "#7c3aed"
                            : chipLabel === "In Repair"
                              ? "#e11d48"
                              : "#0b1220",
                          color: "white",
                          borderRadius: 999,
                          minHeight: 16,
                          fontSize: 8.5,
                        }}
                      >
                        {chipLabel}
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
