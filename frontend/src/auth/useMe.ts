import { useEffect, useState } from "react";
import { apiFetch } from "../api/client";

export type Me = {
  email: string;
  role: "admin" | "user";
};

type State =
  | { status: "loading" }
  | { status: "anonymous" }
  | { status: "authed"; me: Me };

export function useMe() {
  const [state, setState] = useState<State>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;

    apiFetch<Me>("/api/auth/me")
      .then((me) => {
        if (!cancelled) setState({ status: "authed", me });
      })
      .catch(() => {
        if (!cancelled) setState({ status: "anonymous" });
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return state;
}

