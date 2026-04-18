import React from "react";
import Sheet from "@mui/joy/Sheet";
import Table from "@mui/joy/Table";
import Typography from "@mui/joy/Typography";
import AppShell from "../components/AppShell";

export default function MyRentalsPage() {
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
            <tr>
              <td colSpan={5}>
                <Typography level="body-sm" sx={{ color: "neutral.500", textAlign: "center", py: 0.75 }}>
                  You don't have any active rentals
                </Typography>
              </td>
            </tr>
          </tbody>
        </Table>
      </Sheet>
    </AppShell>
  );
}

