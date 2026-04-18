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
import Typography from "@mui/joy/Typography";

type Props = {
  open: boolean;
  onClose: () => void;
  name: string;
  setName: (value: string) => void;
  serial: string;
  setSerial: (value: string) => void;
  brand: string;
  setBrand: (value: string) => void;
  category: string | null;
  setCategory: (value: string | null) => void;
  touched: boolean;
  serialTaken: boolean;
  isSubmitting: boolean;
  submitError: string | null;
  onSubmit: () => void;
};

export default function AddDeviceModal(props: Props) {
  const {
    open,
    onClose,
    name,
    setName,
    serial,
    setSerial,
    brand,
    setBrand,
    category,
    setCategory,
    touched,
    serialTaken,
    isSubmitting,
    submitError,
    onSubmit,
  } = props;

  const trimmedName = name.trim();
  const trimmedSerial = serial.trim();
  const trimmedBrand = brand.trim();

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
          Add New Device
        </Typography>
        <Typography sx={{ color: "#697386", fontSize: 14, mt: 0.4, mb: 1.1 }}>
          Enter the details of the new hardware device
        </Typography>

        <Stack spacing={1.3}>
          <FormControl error={touched && trimmedName.length === 0}>
            <FormLabel sx={{ color: "#111827", fontSize: 14, fontWeight: 600 }}>
              Name
            </FormLabel>
            <Input
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="e.g., MacBook Pro 16"
              sx={{ fontSize: 12, minHeight: 40, borderRadius: 12 }}
            />
          </FormControl>

          <FormControl error={touched && (trimmedSerial.length === 0 || serialTaken)}>
            <FormLabel sx={{ color: "#111827", fontSize: 14, fontWeight: 600 }}>
              Serial Number
            </FormLabel>
            <Input
              value={serial}
              onChange={(event) => setSerial(event.target.value)}
              placeholder="e.g., MBP-2024-001"
              sx={{ fontSize: 12, minHeight: 40, borderRadius: 12 }}
            />
            {touched && serialTaken ? (
              <Typography level="body-xs" color="danger">
                Serial number already exists in the table.
              </Typography>
            ) : null}
          </FormControl>

          <FormControl error={touched && trimmedBrand.length === 0}>
            <FormLabel sx={{ color: "#111827", fontSize: 14, fontWeight: 600 }}>
              Brand
            </FormLabel>
            <Input
              value={brand}
              onChange={(event) => setBrand(event.target.value)}
              placeholder="e.g., Apple"
              sx={{ fontSize: 12, minHeight: 40, borderRadius: 12 }}
            />
          </FormControl>

          <FormControl error={touched && !category}>
            <FormLabel sx={{ color: "#111827", fontSize: 14, fontWeight: 600 }}>
              Category
            </FormLabel>
            <Select
              value={category}
              onChange={(_, value) => setCategory(value)}
              placeholder="Select a category"
              sx={{ fontSize: 12, minHeight: 40, borderRadius: 12 }}
            >
              <Option value="Laptop">Laptop</Option>
              <Option value="Phone">Phone</Option>
              <Option value="Tablet">Tablet</Option>
              <Option value="Peripheral">Peripheral</Option>
              <Option value="Monitor">Monitor</Option>
              <Option value="Other">Other</Option>
            </Select>
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
            Add Device
          </Button>
        </Box>
      </ModalDialog>
    </Modal>
  );
}
