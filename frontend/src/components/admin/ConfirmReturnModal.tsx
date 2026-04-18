import React from "react";
import Box from "@mui/joy/Box";
import Button from "@mui/joy/Button";
import Modal from "@mui/joy/Modal";
import ModalDialog from "@mui/joy/ModalDialog";
import Typography from "@mui/joy/Typography";

type Props = {
  open: boolean;
  isLoading: boolean;
  onCancel: () => void;
  onConfirm: () => void;
};

export default function ConfirmReturnModal(props: Props) {
  const { open, isLoading, onCancel, onConfirm } = props;

  return (
    <Modal open={open} onClose={onCancel}>
      <ModalDialog
        size="sm"
        sx={{
          width: "min(460px, calc(100vw - 24px))",
          borderRadius: "lg",
          borderColor: "#e4e6eb",
          boxShadow: "lg",
          p: 2,
        }}
      >
        <Typography level="h4" sx={{ fontSize: 18, fontWeight: 700, mb: 0.5 }}>
          Confirm Return
        </Typography>
        <Typography sx={{ color: "#697386", fontSize: 13 }}>
          Status is rented. Did the user return the hardware?
        </Typography>
        <Typography sx={{ color: "#697386", fontSize: 13, mt: 0.4 }}>
          If yes, the device will be changed to available.
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
            color="primary"
            loading={isLoading}
            disabled={isLoading}
            onClick={onConfirm}
            sx={{ fontSize: 12, px: 1.6, py: 0.6, borderRadius: 10 }}
          >
            Mark Available
          </Button>
        </Box>
      </ModalDialog>
    </Modal>
  );
}
