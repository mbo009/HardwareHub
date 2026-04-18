import React from "react";
import Box from "@mui/joy/Box";
import Button from "@mui/joy/Button";
import FormControl from "@mui/joy/FormControl";
import FormHelperText from "@mui/joy/FormHelperText";
import FormLabel from "@mui/joy/FormLabel";
import Input from "@mui/joy/Input";
import Sheet from "@mui/joy/Sheet";
import Typography from "@mui/joy/Typography";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../api/client";
import type { Me } from "../auth/useMe";
import PackageIcon from "../components/PackageIcon";

function isBooksyEmail(email: string) {
  const value = email.trim().toLowerCase();
  return value.endsWith("@booksy.com");
}

function getDomainErrorForTyping(email: string): string | null {
  const value = email.trim().toLowerCase();
  const atIndex = value.indexOf("@");

  if (atIndex === -1) return null;

  const domainPart = value.slice(atIndex + 1);
  if (!domainPart) return null;

  if ("booksy.com".startsWith(domainPart)) return null;

  return "Invalid domain. Please use @booksy.com";
}

type LoginPageProps = {
  onLoginSuccess?: (me: Me) => void;
};

export default function LoginPage({ onLoginSuccess }: LoginPageProps) {
  const navigate = useNavigate();
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [submitting, setSubmitting] = React.useState(false);
  const [domainError, setDomainError] = React.useState<string | null>(null);
  const [loginError, setLoginError] = React.useState<string | null>(null);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError(null);

    if (!isBooksyEmail(email)) {
      setDomainError("Invalid domain. Please use @booksy.com");
      return;
    }

    setDomainError(null);
    setSubmitting(true);
    try {
      const me = await apiFetch<Me>("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      onLoginSuccess?.(me);
      navigate("/dashboard", { replace: true });
    } catch {
      setLoginError("Invalid email or password");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        px: 2,
      }}
    >
      <Sheet
        variant="outlined"
        sx={{
          width: 420,
          maxWidth: "100%",
          borderRadius: "lg",
          p: 3,
          boxShadow: "sm",
          bgcolor: "background.surface",
        }}
      >
        <Box sx={{ display: "flex", justifyContent: "flex-start", mb: 1.25 }}>
          <Box
            sx={{
              width: 40,
              height: 40,
              borderRadius: 12,
              display: "grid",
              placeItems: "center",
              bgcolor: "neutral.softBg",
              color: "#5b6473",
              lineHeight: 1,
              transformOrigin: "center center",
              animation: "floaty 6.2s ease-in-out infinite",
              "@keyframes floaty": {
                "0%": { transform: "translate3d(0px, 0px, 0px)" },
                "25%": { transform: "translate3d(0.8px, -1px, 0px)" },
                "50%": { transform: "translate3d(0px, -1.6px, 0px)" },
                "75%": { transform: "translate3d(-0.8px, -0.8px, 0px)" },
                "100%": { transform: "translate3d(0px, 0px, 0px)" },
              },
            }}
          >
            <PackageIcon size={22} color="currentColor" />
          </Box>
        </Box>

        <Typography level="h3" textAlign="center">
          Welcome back
        </Typography>
        <Typography level="body-sm" textAlign="center" sx={{ mt: 0.5, color: "neutral.600" }}>
          Sign in to your account
        </Typography>

        <Box
          component="form"
          onSubmit={onSubmit}
          sx={{
            mt: 2.5,
            display: "flex",
            flexDirection: "column",
            gap: 1.5,
          }}
        >
          <FormControl error={Boolean(domainError)}>
            <FormLabel>Email (company domain only)</FormLabel>
            <Input
              placeholder="name@booksy.com"
              type="email"
              value={email}
              onChange={(ev) => {
                const next = ev.target.value;
                setEmail(next);
                setDomainError(getDomainErrorForTyping(next));
              }}
            />
            {domainError ? (
              <FormHelperText>{domainError}</FormHelperText>
            ) : null}
          </FormControl>

          <FormControl>
            <FormLabel>Password</FormLabel>
            <Input
              placeholder="Enter your password"
              type="password"
              value={password}
              onChange={(ev) => setPassword(ev.target.value)}
            />
          </FormControl>

          {loginError ? (
            <Typography level="body-sm" sx={{ color: "danger.600" }}>
              {loginError}
            </Typography>
          ) : null}

          <Button
            type="submit"
            loading={submitting}
            sx={{
              mt: 1,
              borderRadius: "md",
              bgcolor: "#0b1220",
              ":hover": { bgcolor: "#0b1220" },
            }}
          >
            Login
          </Button>
        </Box>
      </Sheet>
    </Box>
  );
}

