import React from "react";
import Box from "@mui/joy/Box";
import Button from "@mui/joy/Button";
import Checkbox from "@mui/joy/Checkbox";
import FormControl from "@mui/joy/FormControl";
import FormLabel from "@mui/joy/FormLabel";
import Input from "@mui/joy/Input";
import Modal from "@mui/joy/Modal";
import ModalClose from "@mui/joy/ModalClose";
import ModalDialog from "@mui/joy/ModalDialog";
import Typography from "@mui/joy/Typography";

type Props = {
  open: boolean;
  email: string;
  setEmail: (value: string) => void;
  adminPrivileges: boolean;
  setAdminPrivileges: (value: boolean) => void;
  isSubmitting: boolean;
  submitError: string | null;
  generatedPassword: string | null;
  onClose: () => void;
  onSubmit: () => void;
};

export default function CreateUserModal(props: Props) {
  const {
    open,
    email,
    setEmail,
    adminPrivileges,
    setAdminPrivileges,
    isSubmitting,
    submitError,
    generatedPassword,
    onClose,
    onSubmit,
  } = props;

  return (
    <Modal open={open} onClose={onClose}>
      <ModalDialog
        size="md"
        sx={{
          width: "min(560px, calc(100vw - 24px))",
          borderRadius: "lg",
          borderColor: "#e4e6eb",
          boxShadow: "lg",
          px: { xs: 2, sm: 3 },
          py: { xs: 2, sm: 2.5 },
        }}
      >
        <ModalClose sx={{ mt: 0.5, mr: 0.5 }} />
        <Typography level="h3" sx={{ fontSize: 24, fontWeight: 700 }}>
          Create User
        </Typography>
        <Typography sx={{ color: "#697386", fontSize: 14, mt: 0.4, mb: 1.1 }}>
          Enter user email. Temporary password will be generated automatically.
        </Typography>

        <FormControl>
          <FormLabel sx={{ color: "#111827", fontSize: 14, fontWeight: 600 }}>
            User email
          </FormLabel>
          <Input
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="new.user@booksy.com"
            type="email"
            sx={{ fontSize: 12, minHeight: 40, borderRadius: 12 }}
          />
        </FormControl>

        <FormControl sx={{ mt: 1 }}>
          <Checkbox
            size="sm"
            checked={adminPrivileges}
            onChange={(event) => setAdminPrivileges(event.target.checked)}
            label={
              <Typography sx={{ fontSize: 13, fontWeight: 600, color: "#111827" }}>
                Admin privileges
              </Typography>
            }
            slotProps={{
              label: { sx: { ml: 0.5 } },
            }}
          />
          <Typography level="body-xs" sx={{ mt: 0.35, ml: 3.2, color: "#6b7280" }}>
            New user can access Admin Panel and manage hardware and accounts.
          </Typography>
        </FormControl>

        {generatedPassword ? (
          <Box
            sx={{
              mt: 1.2,
              p: 1,
              borderRadius: "sm",
              border: "1px solid #e5e7eb",
              bgcolor: "#f8fafc",
            }}
          >
            <Typography level="body-xs" sx={{ fontWeight: 600, color: "#111827" }}>
              Temporary password
            </Typography>
            <Typography
              level="body-sm"
              sx={{ mt: 0.4, fontFamily: "monospace", color: "#0b1220" }}
            >
              {generatedPassword}
            </Typography>
            <Typography level="body-xs" sx={{ mt: 0.35, color: "#6b7280" }}>
              User must change it after first login.
            </Typography>
          </Box>
        ) : null}

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
            Close
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
            Generate temporary password
          </Button>
        </Box>
      </ModalDialog>
    </Modal>
  );
}
