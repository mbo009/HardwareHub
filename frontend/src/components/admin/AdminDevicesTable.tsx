import React from "react";
import Box from "@mui/joy/Box";
import Chip from "@mui/joy/Chip";
import IconButton from "@mui/joy/IconButton";
import Sheet from "@mui/joy/Sheet";
import Table from "@mui/joy/Table";
import Typography from "@mui/joy/Typography";
import { EditIcon, TrashIcon, WrenchIcon } from "./icons";
import type { Row } from "./types";

type Props = {
  rows: Row[];
  isLoadingRows: boolean;
  loadRowsError: string | null;
  deleteError: string | null;
  repairError: string | null;
  repairNotice: string | null;
  deletingSerial: string | null;
  repairingSerial: string | null;
  onRequestDelete: (row: Row) => void;
  onRepair: (row: Row) => void;
  onRequestReturn: (row: Row) => void;
  sortBy: "name" | "brand" | "serial" | "purchaseDate" | "status";
  sortOrder: "asc" | "desc";
  onSort: (field: "name" | "brand" | "serial" | "purchaseDate" | "status") => void;
};

export default function AdminDevicesTable(props: Props) {
  const {
    rows,
    isLoadingRows,
    loadRowsError,
    deleteError,
    repairError,
    repairNotice,
    deletingSerial,
    repairingSerial,
    onRequestDelete,
    onRepair,
    onRequestReturn,
    sortBy,
    sortOrder,
    onSort,
  } = props;

  const labelFor = (
    field: "name" | "brand" | "serial" | "purchaseDate" | "status",
    label: string,
  ) => {
    const active = sortBy === field;
    const arrow = !active ? "" : sortOrder === "asc" ? " ↑" : " ↓";
    return (
      <button
        type="button"
        onClick={() => onSort(field)}
        style={{
          border: "none",
          background: "transparent",
          padding: 0,
          margin: 0,
          font: "inherit",
          color: "inherit",
          cursor: "pointer",
        }}
      >
        {label}
        {arrow}
      </button>
    );
  };

  return (
    <Sheet
      variant="outlined"
      sx={{ borderRadius: "md", overflow: "hidden", width: "100%", maxWidth: 790, borderColor: "#e9ebf0" }}
    >
      {deleteError ? (
        <Typography level="body-sm" color="danger" sx={{ px: 1, py: 0.6 }}>
          {deleteError}
        </Typography>
      ) : null}
      {repairError ? (
        <Typography level="body-sm" color="danger" sx={{ px: 1, py: 0.6 }}>
          {repairError}
        </Typography>
      ) : null}
      {repairNotice ? (
        <Typography level="body-sm" color="warning" sx={{ px: 1, py: 0.6 }}>
          {repairNotice}
        </Typography>
      ) : null}
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
            <th>{labelFor("name", "Device Name")}</th>
            <th>{labelFor("brand", "Brand")}</th>
            <th>{labelFor("serial", "Serial Number")}</th>
            <th>{labelFor("purchaseDate", "Date Added")}</th>
            <th>{labelFor("status", "Status")}</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {isLoadingRows ? (
            <tr>
              <td colSpan={6}>Loading...</td>
            </tr>
          ) : loadRowsError ? (
            <tr>
              <td colSpan={6}>{loadRowsError}</td>
            </tr>
          ) : rows.length === 0 ? (
            <tr>
              <td colSpan={6}>No devices found.</td>
            </tr>
          ) : (
            rows.map((row) => (
              <tr key={row.serial}>
                <td>{row.name}</td>
                <td>{row.brand}</td>
                <td>{row.serial}</td>
                <td>{row.date}</td>
                <td>
                  <Chip
                    size="sm"
                    sx={{
                      bgcolor:
                        row.status === "In Repair"
                          ? "#e11d48"
                          : row.status === "Unknown"
                            ? "#6b7280"
                            : "#0b1220",
                      color: "white",
                      borderRadius: 999,
                      minHeight: 16,
                      fontSize: 8.5,
                    }}
                  >
                    {row.status}
                  </Chip>
                </td>
                <td>
                  <Box sx={{ display: "inline-flex", alignItems: "center", gap: 0.35 }}>
                    <IconButton
                      size="sm"
                      variant="plain"
                      color="neutral"
                      aria-label="Edit device"
                      sx={{ "--IconButton-size": "18px", color: "#111827" }}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="sm"
                      variant="plain"
                      color="neutral"
                      aria-label="Service device"
                      loading={repairingSerial === row.serial}
                      disabled={repairingSerial === row.serial}
                      onClick={() => {
                        if (row.status === "Rented") {
                          onRequestReturn(row);
                          return;
                        }
                        onRepair(row);
                      }}
                      sx={{ "--IconButton-size": "18px", color: "#111827" }}
                    >
                      <WrenchIcon />
                    </IconButton>
                    <IconButton
                      size="sm"
                      variant="plain"
                      color="danger"
                      aria-label="Delete device"
                      loading={deletingSerial === row.serial}
                      disabled={deletingSerial === row.serial}
                      onClick={() => onRequestDelete(row)}
                      sx={{ "--IconButton-size": "18px" }}
                    >
                      <TrashIcon />
                    </IconButton>
                  </Box>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </Table>
    </Sheet>
  );
}
