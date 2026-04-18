import React from "react";
import Box from "@mui/joy/Box";
import Button from "@mui/joy/Button";
import Modal from "@mui/joy/Modal";
import ModalDialog from "@mui/joy/ModalDialog";
import Typography from "@mui/joy/Typography";
import type { Row } from "./types";

type Props = {
  open: boolean;
  row: Row | null;
  isLoading: boolean;
  onCancel: () => void;
  onConfirm: () => void;
};

export default function ConfirmDeleteModal(props: Props) {
  const { open, row, isLoading, onCancel, onConfirm } = props;

  return (
    <Modal open={open} onClose={onCancel}>
      <ModalDialog
        size="sm"
        sx={{
          width: "min(420px, calc(100vw - 24px))",
          borderRadius: "lg",
          borderColor: "#e4e6eb",
          boxShadow: "lg",
          p: 2,
        }}
      >
        <Typography level="h4" sx={{ fontSize: 18, fontWeight: 700, mb: 0.5 }}>
          Delete Device
        </Typography>
        <Typography sx={{ color: "#697386", fontSize: 13 }}>
          Are you sure you want to delete{" "}
          <Typography component="span" sx={{ fontWeight: 700, color: "#111827" }}>
            {row?.name || "this device"}
          </Typography>
          ? This action cannot be undone.
        </Typography>

        <Box sx={{ mt: 1.8, display: "flex", justifyContent: "flex-end", gap: 1 }}>
          <Button
            variant="outlined"
            color="neutral"
            onClick={onCancel}
            disabled={isLoading}
            sx={{ fontSize: 12, px: 1.6, py: 0.6, borderRadius: 10 }}
          >
            Cancel
          </Button>
          <Button
            color="danger"
            loading={isLoading}
            disabled={isLoading}
            onClick={onConfirm}
            sx={{ fontSize: 12, px: 1.6, py: 0.6, borderRadius: 10 }}
          >
            Delete
          </Button>
        </Box>
      </ModalDialog>
    </Modal>
  );
}
