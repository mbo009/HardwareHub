import { useCallback, useEffect, useState } from "react";
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

  const refresh = useCallback(async () => {
    apiFetch<Me>("/api/auth/me")
      .then((me) => {
        setState({ status: "authed", me });
      })
      .catch(() => {
        setState({ status: "anonymous" });
      });
  }, []);

  const setAuthed = useCallback((me: Me) => {
    setState({ status: "authed", me });
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return { state, refresh, setAuthed };
}

