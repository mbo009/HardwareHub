import React from "react";
import Box from "@mui/joy/Box";
import Button from "@mui/joy/Button";
import FormControl from "@mui/joy/FormControl";
import FormHelperText from "@mui/joy/FormHelperText";
import FormLabel from "@mui/joy/FormLabel";
import Input from "@mui/joy/Input";
import Modal from "@mui/joy/Modal";
import ModalDialog from "@mui/joy/ModalDialog";
import Typography from "@mui/joy/Typography";

type Props = {
  open: boolean;
  isSubmitting: boolean;
  error: string | null;
  onSubmit: (newPassword: string) => void;
};

export default function ForcePasswordChangeModal(props: Props) {
  const { open, isSubmitting, error, onSubmit } = props;
  const [newPassword, setNewPassword] = React.useState("");
  const [confirmPassword, setConfirmPassword] = React.useState("");

  const passwordsMismatch =
    confirmPassword.length > 0 && newPassword !== confirmPassword;

  return (
    <Modal open={open}>
      <ModalDialog
        size="md"
        sx={{
          width: "min(520px, calc(100vw - 24px))",
          borderRadius: "lg",
          borderColor: "#e4e6eb",
          boxShadow: "lg",
          px: { xs: 2, sm: 3 },
          py: { xs: 2, sm: 2.5 },
        }}
      >
        <Typography level="h3" sx={{ fontSize: 24, fontWeight: 700 }}>
          Set New Password
        </Typography>
        <Typography sx={{ color: "#697386", fontSize: 14, mt: 0.4, mb: 1.1 }}>
          First login detected. You must set your own password to continue.
        </Typography>

        <Box sx={{ display: "flex", flexDirection: "column", gap: 1.3 }}>
          <FormControl>
            <FormLabel sx={{ color: "#111827", fontSize: 14, fontWeight: 600 }}>
              New password
            </FormLabel>
            <Input
              type="password"
              value={newPassword}
              onChange={(event) => setNewPassword(event.target.value)}
              placeholder="Strong password"
              sx={{ fontSize: 12, minHeight: 40, borderRadius: 12 }}
            />
          </FormControl>

          <FormControl error={passwordsMismatch}>
            <FormLabel sx={{ color: "#111827", fontSize: 14, fontWeight: 600 }}>
              Confirm password
            </FormLabel>
            <Input
              type="password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              placeholder="Repeat password"
              sx={{ fontSize: 12, minHeight: 40, borderRadius: 12 }}
            />
            {passwordsMismatch ? (
              <FormHelperText>Passwords do not match.</FormHelperText>
            ) : null}
          </FormControl>
        </Box>

        {error ? (
          <Typography level="body-sm" color="danger" sx={{ mt: 1 }}>
            {error}
          </Typography>
        ) : null}

        <Box sx={{ mt: 1.6, display: "flex", justifyContent: "flex-end" }}>
          <Button
            onClick={() => {
              if (!newPassword || passwordsMismatch) {
                return;
              }
              onSubmit(newPassword);
            }}
            loading={isSubmitting}
            disabled={isSubmitting || !newPassword || passwordsMismatch}
            sx={{
              bgcolor: "#030a2b",
              ":hover": { bgcolor: "#030a2b" },
              fontSize: 12,
              px: 1.8,
              py: 0.7,
              borderRadius: 12,
            }}
          >
            Save new password
          </Button>
        </Box>
      </ModalDialog>
    </Modal>
  );
}
