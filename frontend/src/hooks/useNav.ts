import { useEffect, useState } from "react";
import { ds } from "./useMeta";
import type { NavTree } from "../lib/types";

export function useNav() {
  const [nav, setNav] = useState<NavTree | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    ds.getNav()
      .then((n) => active && setNav(n))
      .catch((e) => active && setError(String(e)));
    return () => {
      active = false;
    };
  }, []);

  return { nav, error };
}
