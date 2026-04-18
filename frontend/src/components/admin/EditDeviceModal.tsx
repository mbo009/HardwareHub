import React from "react";
import Box from "@mui/joy/Box";
import Button from "@mui/joy/Button";
import FormControl from "@mui/joy/FormControl";
import FormLabel from "@mui/joy/FormLabel";
import Input from "@mui/joy/Input";
import Modal from "@mui/joy/Modal";
import ModalClose from "@mui/joy/ModalClose";
import ModalDialog from "@mui/joy/ModalDialog";
import Option from "@mui/joy/Option";
import Select from "@mui/joy/Select";
import Stack from "@mui/joy/Stack";
import Textarea from "@mui/joy/Textarea";
import Typography from "@mui/joy/Typography";
import type { Row } from "./types";

type EditableStatus = Row["status"];

type Props = {
  open: boolean;
  row: Row | null;
  name: string;
  setName: (value: string) => void;
  brand: string;
  setBrand: (value: string) => void;
  serial: string;
  setSerial: (value: string) => void;
  notes: string;
  setNotes: (value: string) => void;
  assignedTo: string;
  setAssignedTo: (value: string) => void;
  status: EditableStatus;
  setStatus: (value: EditableStatus) => void;
  isSubmitting: boolean;
  submitError: string | null;
  onClose: () => void;
  onSubmit: () => void;
};

export default function EditDeviceModal(props: Props) {
  const {
    open,
    row,
    name,
    setName,
    brand,
    setBrand,
    serial,
    setSerial,
    notes,
    setNotes,
    assignedTo,
    setAssignedTo,
    status,
    setStatus,
    isSubmitting,
    submitError,
    onClose,
    onSubmit,
  } = props;

  return (
    <Modal open={open} onClose={onClose}>
      <ModalDialog
        size="lg"
        sx={{
          width: "min(730px, calc(100vw - 24px))",
          borderRadius: "lg",
          borderColor: "#e4e6eb",
          boxShadow: "lg",
          px: { xs: 2, sm: 3 },
          py: { xs: 2, sm: 2.5 },
        }}
      >
        <ModalClose sx={{ mt: 0.5, mr: 0.5 }} />

        <Typography level="h3" sx={{ fontSize: 26, fontWeight: 700 }}>
          Edit Device
        </Typography>
        <Typography sx={{ color: "#697386", fontSize: 14, mt: 0.4, mb: 1.1 }}>
          Update details for {row?.name || "selected device"}
        </Typography>

        <Stack spacing={1.3}>
          <FormControl>
            <FormLabel sx={{ color: "#111827", fontSize: 14, fontWeight: 600 }}>
              Name
            </FormLabel>
            <Input
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Device name"
              sx={{ fontSize: 12, minHeight: 40, borderRadius: 12 }}
            />
          </FormControl>

          <FormControl>
            <FormLabel sx={{ color: "#111827", fontSize: 14, fontWeight: 600 }}>
              Brand
            </FormLabel>
            <Input
              value={brand}
              onChange={(event) => setBrand(event.target.value)}
              placeholder="Brand"
              sx={{ fontSize: 12, minHeight: 40, borderRadius: 12 }}
            />
          </FormControl>

          <FormControl>
            <FormLabel sx={{ color: "#111827", fontSize: 14, fontWeight: 600 }}>
              Serial Number
            </FormLabel>
            <Input
              value={serial}
              onChange={(event) => setSerial(event.target.value)}
              placeholder="Serial number (optional)"
              sx={{ fontSize: 12, minHeight: 40, borderRadius: 12 }}
            />
          </FormControl>

          <FormControl>
            <FormLabel sx={{ color: "#111827", fontSize: 14, fontWeight: 600 }}>
              Assign to user (email)
            </FormLabel>
            <Input
              value={assignedTo}
              onChange={(event) => {
                const value = event.target.value;
                setAssignedTo(value);
                if (value.trim()) {
                  setStatus("Rented");
                }
              }}
              placeholder="user@booksy.com"
              sx={{ fontSize: 12, minHeight: 40, borderRadius: 12 }}
            />
            <Typography level="body-xs" sx={{ mt: 0.35, color: "#6b7280" }}>
              Filling email auto-sets status to Rented.
            </Typography>
          </FormControl>

          <FormControl>
            <FormLabel sx={{ color: "#111827", fontSize: 14, fontWeight: 600 }}>
              Status
            </FormLabel>
            <Select
              value={status}
              onChange={(_, value) => {
                if (!value) return;
                setStatus(value as EditableStatus);
              }}
              sx={{ fontSize: 12, minHeight: 40, borderRadius: 12 }}
            >
              <Option value="Available">Available</Option>
              <Option value="Rented">Rented</Option>
              <Option value="In Repair">In Repair</Option>
              <Option value="Unknown">Unknown</Option>
            </Select>
          </FormControl>

          <FormControl>
            <FormLabel sx={{ color: "#111827", fontSize: 14, fontWeight: 600 }}>
              Notes
            </FormLabel>
            <Textarea
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
              placeholder="Optional notes..."
              minRows={3}
              sx={{ fontSize: 12, borderRadius: 12 }}
            />
          </FormControl>
        </Stack>

        {submitError ? (
          <Typography level="body-sm" color="danger" sx={{ mt: 1 }}>
            {submitError}
          </Typography>
        ) : null}

        <Box sx={{ mt: 1.6, display: "flex", justifyContent: "flex-end", gap: 1 }}>
          <Button
            variant="outlined"
            color="neutral"
            onClick={onClose}
            disabled={isSubmitting}
            sx={{ fontSize: 12, px: 1.8, py: 0.7, borderRadius: 12 }}
          >
            Cancel
          </Button>
          <Button
            onClick={onSubmit}
            loading={isSubmitting}
            disabled={isSubmitting}
            sx={{
              bgcolor: "#030a2b",
              ":hover": { bgcolor: "#030a2b" },
              fontSize: 12,
              px: 1.8,
              py: 0.7,
              borderRadius: 12,
            }}
          >
            Save Changes
          </Button>
        </Box>
      </ModalDialog>
    </Modal>
  );
}
