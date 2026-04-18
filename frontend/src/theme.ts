import { extendTheme } from "@mui/joy/styles";

export const theme = extendTheme({
  fontFamily: {
    body: "Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif",
    display: "Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif",
  },
  colorSchemes: {
    light: {
      palette: {
        background: {
          body: "#f6f7fb",
          surface: "#ffffff",
        },
      },
    },
  },
  radius: {
    md: "14px",
    lg: "16px",
  },
  components: {
    JoyInput: {
      styleOverrides: {
        root: {
          "--Input-focusedThickness": "0px",
          "--Input-focusedHighlight": "0 0 #0000",
          backgroundColor: "#f3f4f6",
          borderColor: "#e5e7eb",
          boxShadow: "none",
          transition:
            "box-shadow 340ms cubic-bezier(0.22, 1, 0.36, 1), border-color 260ms cubic-bezier(0.22, 1, 0.36, 1), background-color 260ms cubic-bezier(0.22, 1, 0.36, 1)",
          "&:hover": {
            borderColor: "#d1d5db",
          },
          "&:focus-within": {
            borderColor: "#d6d9df",
            boxShadow: "0 0 0 6px rgba(148, 163, 184, 0.16)",
          },
        },
        input: {
          "&:focus": {
            outline: "none",
          },
          "::placeholder": {
            color: "#9ca3af",
            opacity: 1,
          },
        },
      },
    },
  },
});

