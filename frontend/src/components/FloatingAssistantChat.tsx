import React from "react";
import Alert from "@mui/joy/Alert";
import Box from "@mui/joy/Box";
import Button from "@mui/joy/Button";
import Chip from "@mui/joy/Chip";
import IconButton from "@mui/joy/IconButton";
import Input from "@mui/joy/Input";
import Sheet from "@mui/joy/Sheet";
import Typography from "@mui/joy/Typography";
import { apiFetch, type ApiError } from "../api/client";
import { emitHardwareInventoryChanged } from "../hardware/inventoryEvents";

type ChatRole = "user" | "assistant";

type ChatMessage = {
  role: ChatRole;
  content: string;
};

export type AssistantProposal = {
  suggestAdd: boolean;
  name: string;
  brand: string;
  serialNumber: string | null;
  purchaseDate: string | null;
  notes: string | null;
  status: string;
  missingFields: string[];
};

type ChatResponse = {
  message: string;
  proposal: AssistantProposal | null;
};

type AssistantSettings = {
  provider: string;
  model: string;
  ollamaBaseUrl: string | null;
  ollamaImageMode: string | null;
  imagesSupported: boolean;
};

type Props = {
  email: string | null;
  role: "admin" | "user" | null;
};

function localPartFromEmail(email: string): string {
  const at = email.indexOf("@");
  return at === -1 ? email : email.slice(0, at);
}

function readFileAsDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => resolve(String(r.result));
    r.onerror = () => reject(new Error("read failed"));
    r.readAsDataURL(file);
  });
}

export default function FloatingAssistantChat(props: Props) {
  const { email, role } = props;
  const [open, setOpen] = React.useState(false);
  const [messages, setMessages] = React.useState<ChatMessage[]>([]);
  const [draft, setDraft] = React.useState("");
  const [pendingImages, setPendingImages] = React.useState<string[]>([]);
  const [proposal, setProposal] = React.useState<AssistantProposal | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [addBusy, setAddBusy] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [assistantSettings, setAssistantSettings] =
    React.useState<AssistantSettings | null>(null);
  const fileRef = React.useRef<HTMLInputElement | null>(null);
  const scrollRef = React.useRef<HTMLDivElement | null>(null);

  React.useEffect(() => {
    setMessages([]);
    setProposal(null);
    setPendingImages([]);
    setDraft("");
  }, [email]);

  React.useEffect(() => {
    if (!open || !email) return;
    setMessages((prev) => {
      if (prev.length > 0) return prev;
      return [
        {
          role: "assistant",
          content: `Hello ${localPartFromEmail(email.trim())}, how can I help you :)`,
        },
      ];
    });
  }, [open, email]);

  React.useEffect(() => {
    if (!open || !email) return;
    let cancelled = false;
    apiFetch<AssistantSettings>("/api/assistant/settings")
      .then((s) => {
        if (!cancelled) setAssistantSettings(s);
      })
      .catch(() => {
        if (!cancelled) setAssistantSettings(null);
      });
    return () => {
      cancelled = true;
    };
  }, [open, email]);

  React.useEffect(() => {
    if (!scrollRef.current) return;
    scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, loading, proposal]);

  if (!email) {
    return null;
  }

  const isAdmin = role === "admin";

  async function onPickFiles(files: FileList | null) {
    if (!files?.length) return;
    const next: string[] = [...pendingImages];
    for (let i = 0; i < files.length && next.length < 4; i++) {
      const f = files[i];
      if (!f.type.startsWith("image/")) continue;
      if (f.size > 4 * 1024 * 1024) continue;
      try {
        next.push(await readFileAsDataUrl(f));
      } catch {
        /* skip */
      }
    }
    setPendingImages(next);
    if (fileRef.current) fileRef.current.value = "";
  }

  async function sendMessage() {
    const text = draft.trim();
    if (!text && pendingImages.length === 0) return;
    setError(null);
    const userContent =
      text || (pendingImages.length ? "Here are photos of the device." : "");
    const history = [...messages, { role: "user" as const, content: userContent }];
    setMessages(history);
    setDraft("");
    const imgs = [...pendingImages];
    setPendingImages([]);
    setLoading(true);
    try {
      const res = await apiFetch<ChatResponse>("/api/assistant/chat", {
        method: "POST",
        body: JSON.stringify({
          messages: history,
          images: imgs.length ? imgs : undefined,
        }),
      });
      setMessages((m) => [...m, { role: "assistant", content: res.message }]);
      setProposal((prev) => res.proposal ?? prev);
    } catch (err) {
      const apiErr = err as ApiError;
      if (apiErr?.status === 401) {
        setError("Session expired. Log in again.");
      } else {
        setError("Could not reach the assistant. Try again.");
      }
      setMessages((m) => m.slice(0, -1));
      setPendingImages(imgs);
      setDraft(text);
    } finally {
      setLoading(false);
    }
  }

  async function addProposalToInventory() {
    if (!proposal || !proposal.suggestAdd) return;
    setError(null);
    setAddBusy(true);
    try {
      await apiFetch("/api/admin/hardware", {
        method: "POST",
        body: JSON.stringify({
          name: proposal.name,
          brand: proposal.brand,
          serialNumber: proposal.serialNumber || null,
          status: proposal.status || "Available",
          purchaseDate: proposal.purchaseDate || new Date().toISOString().slice(0, 10),
          notes: proposal.notes || null,
          history: "Created via AI assistant",
        }),
      });
      emitHardwareInventoryChanged();
      setProposal(null);
      setMessages([
        {
          role: "assistant",
          content:
            "Saved to inventory. Add another device anytime — new photos or a short description.",
        },
      ]);
    } catch (err) {
      const apiErr = err as ApiError;
      if (apiErr?.status === 403) {
        setError("Only admins can add devices.");
      } else if (apiErr?.status === 400) {
        setError("Could not add — check required fields (name, brand).");
      } else {
        setError("Add failed. Try from the admin panel.");
      }
    } finally {
      setAddBusy(false);
    }
  }

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
            width: "min(380px, calc(100vw - 40px))",
            height: 520,
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
            ref={scrollRef}
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
            {messages.map((msg, idx) => (
              <Box
                key={`${idx}-${msg.role}-${msg.content.slice(0, 12)}`}
                sx={{
                  alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
                  maxWidth: "92%",
                  px: 1.25,
                  py: 0.85,
                  borderRadius:
                    msg.role === "user"
                      ? "14px 14px 4px 14px"
                      : "14px 14px 14px 4px",
                  bgcolor: msg.role === "user" ? "#030a2b" : "#f1f5f9",
                  border: msg.role === "user" ? "none" : "1px solid #e2e8f0",
                }}
              >
                <Typography
                  level="body-sm"
                  sx={{
                    color: msg.role === "user" ? "#fff" : "#1f2937",
                    fontSize: 13,
                    whiteSpace: "pre-wrap",
                  }}
                >
                  {msg.content}
                </Typography>
              </Box>
            ))}
            {loading ? (
              <Typography level="body-xs" sx={{ color: "#6b7280", px: 0.5 }}>
                Thinking…
              </Typography>
            ) : null}

            {proposal && proposal.suggestAdd ? (
              <Box
                sx={{
                  mt: 0.5,
                  p: 1.25,
                  borderRadius: "md",
                  bgcolor: "#faf5ff",
                  border: "1px solid #e9d5ff",
                }}
              >
                <Typography level="title-sm" sx={{ mb: 0.75, fontWeight: 700 }}>
                  Suggested device
                </Typography>
                <Typography level="body-xs" sx={{ color: "#4b5563", mb: 0.5 }}>
                  <strong>Name:</strong> {proposal.name}
                </Typography>
                <Typography level="body-xs" sx={{ color: "#4b5563", mb: 0.5 }}>
                  <strong>Brand:</strong> {proposal.brand}
                </Typography>
                <Typography level="body-xs" sx={{ color: "#4b5563", mb: 0.5 }}>
                  <strong>Serial:</strong> {proposal.serialNumber || "—"}
                </Typography>
                <Typography level="body-xs" sx={{ color: "#4b5563", mb: 0.75 }}>
                  <strong>Status:</strong> {proposal.status}
                </Typography>
                {proposal.missingFields?.length ? (
                  <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5, mb: 1 }}>
                    {proposal.missingFields.map((f) => (
                      <Chip key={f} size="sm" variant="soft" color="warning">
                        Need: {f}
                      </Chip>
                    ))}
                  </Box>
                ) : null}
                {isAdmin ? (
                  <Button
                    size="sm"
                    loading={addBusy}
                    disabled={addBusy}
                    onClick={() => void addProposalToInventory()}
                    sx={{
                      mt: 0.5,
                      bgcolor: "#7c3aed",
                      ":hover": { bgcolor: "#6d28d9" },
                    }}
                  >
                    Add to inventory
                  </Button>
                ) : (
                  <Typography level="body-xs" sx={{ color: "#6b7280" }}>
                    Only admins can add devices. Ask an admin to add this entry.
                  </Typography>
                )}
              </Box>
            ) : null}

            {error ? (
              <Typography level="body-xs" color="danger">
                {error}
              </Typography>
            ) : null}
          </Box>

          <Box sx={{ p: 1.25, borderTop: "1px solid #e9ebf0", bgcolor: "#fafafa" }}>
            {assistantSettings &&
            !assistantSettings.imagesSupported &&
            pendingImages.length > 0 ? (
              <Alert
                size="sm"
                variant="soft"
                color="warning"
                sx={{ mb: 0.75, fontSize: 11 }}
              >
                {assistantSettings.provider === "ollama"
                  ? `Photos are not analyzed with this text-only model (${assistantSettings.model}). Use a vision model (e.g. ollama pull llava:7b, then OLLAMA_MODEL=llava:7b), set OLLAMA_IMAGE_MODE=vision if your tag is not detected, or describe the device in text.`
                  : `Photos are not analyzed with this model (${assistantSettings.model}). Describe the device in text or configure a vision-capable model on the server.`}
              </Alert>
            ) : null}
            {pendingImages.length ? (
              <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5, mb: 0.75 }}>
                {pendingImages.map((src, i) => (
                  <Box
                    key={i}
                    component="img"
                    src={src}
                    alt=""
                    sx={{
                      width: 44,
                      height: 44,
                      objectFit: "cover",
                      borderRadius: "sm",
                      border: "1px solid #e5e7eb",
                    }}
                  />
                ))}
                <Button size="sm" variant="plain" onClick={() => setPendingImages([])}>
                  Clear photos
                </Button>
              </Box>
            ) : null}
            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              multiple
              hidden
              onChange={(e) => void onPickFiles(e.target.files)}
            />
            <Box sx={{ display: "flex", gap: 0.6, alignItems: "center" }}>
              <Button
                size="sm"
                variant="outlined"
                color="neutral"
                onClick={() => fileRef.current?.click()}
                disabled={loading || pendingImages.length >= 4}
              >
                Photo
              </Button>
              <Input
                size="sm"
                placeholder="Describe the device or ask…"
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                disabled={loading}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    void sendMessage();
                  }
                }}
                sx={{
                  flex: 1,
                  borderRadius: "lg",
                  fontSize: 13,
                }}
              />
              <Button
                size="sm"
                disabled={loading || (!draft.trim() && pendingImages.length === 0)}
                onClick={() => void sendMessage()}
                sx={{ bgcolor: "#030a2b", ":hover": { bgcolor: "#0f1a4a" } }}
              >
                Send
              </Button>
            </Box>
          </Box>
        </Sheet>
      ) : null}
    </>
  );
}
