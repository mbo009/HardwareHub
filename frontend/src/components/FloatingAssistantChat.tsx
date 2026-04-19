import React from "react";
import Box from "@mui/joy/Box";
import IconButton from "@mui/joy/IconButton";
import Input from "@mui/joy/Input";
import Sheet from "@mui/joy/Sheet";
import Typography from "@mui/joy/Typography";

type Props = {
  /** Logged-in user email; widget hidden when null */
  email: string | null;
};

function localPartFromEmail(email: string): string {
  const at = email.indexOf("@");
  return at === -1 ? email : email.slice(0, at);
}

export default function FloatingAssistantChat(props: Props) {
  const { email } = props;
  const [open, setOpen] = React.useState(false);

  if (!email) {
    return null;
  }

  const displayName = localPartFromEmail(email.trim()) || "there";

  return (
    <>
      <IconButton
        variant="solid"
        onClick={() => setOpen((v) => !v)}
        aria-label={open ? "Close assistant" : "Open assistant"}
        sx={{
          position: "fixed",
          right: 20,
          bottom: 20,
          zIndex: 1200,
          width: 56,
          height: 56,
          borderRadius: "50%",
          bgcolor: "#030a2b",
          boxShadow: "0 4px 14px rgba(3, 10, 43, 0.35)",
          ":hover": { bgcolor: "#0f1a4a" },
        }}
      >
        <Typography sx={{ fontSize: 22, lineHeight: 1 }}>💬</Typography>
      </IconButton>

      {open ? (
        <Sheet
          variant="outlined"
          sx={{
            position: "fixed",
            right: 20,
            bottom: 88,
            zIndex: 1200,
            width: "min(360px, calc(100vw - 40px))",
            height: 420,
            maxHeight: "calc(100vh - 120px)",
            borderRadius: "16px",
            overflow: "hidden",
            display: "flex",
            flexDirection: "column",
            borderColor: "#e4e6eb",
            boxShadow: "0 8px 32px rgba(15, 23, 42, 0.12)",
          }}
        >
          <Box
            sx={{
              px: 1.5,
              py: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              bgcolor: "#f8fafc",
              borderBottom: "1px solid #e9ebf0",
            }}
          >
            <Typography level="title-sm" sx={{ fontWeight: 700, color: "#111827" }}>
              Assistant
            </Typography>
            <IconButton
              size="sm"
              variant="plain"
              onClick={() => setOpen(false)}
              aria-label="Close"
              sx={{ "--IconButton-size": "32px", color: "#6b7280" }}
            >
              <Typography sx={{ fontSize: 20, lineHeight: 1 }}>×</Typography>
            </IconButton>
          </Box>

          <Box
            sx={{
              flex: 1,
              overflowY: "auto",
              p: 1.5,
              bgcolor: "#fff",
              display: "flex",
              flexDirection: "column",
              gap: 1,
            }}
          >
            <Box
              sx={{
                alignSelf: "flex-start",
                maxWidth: "92%",
                px: 1.25,
                py: 0.85,
                borderRadius: "14px 14px 14px 4px",
                bgcolor: "#f1f5f9",
                border: "1px solid #e2e8f0",
              }}
            >
              <Typography level="body-sm" sx={{ color: "#1f2937", fontSize: 13 }}>
                Hello {displayName}, how can I help you :)
              </Typography>
            </Box>
          </Box>

          <Box sx={{ p: 1.25, borderTop: "1px solid #e9ebf0", bgcolor: "#fafafa" }}>
            <Input
              size="sm"
              placeholder="Type a message…"
              disabled
              sx={{
                borderRadius: "lg",
                fontSize: 13,
                "--Input-placeholderOpacity": 0.55,
              }}
            />
          </Box>
        </Sheet>
      ) : null}
    </>
  );
}
