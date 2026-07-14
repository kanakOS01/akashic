import { useCallback, useEffect, useState } from "react";
import { ds } from "./useMeta";
import type { DocRecord } from "../lib/types";

export function useDoc(path: string | undefined) {
  const [doc, setDoc] = useState<DocRecord | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    if (!path) {
      setDoc(null);
      return;
    }
    setLoading(true);
    setError(null);
    ds.getDoc(path)
      .then((d) => setDoc(d))
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, [path]);

  useEffect(() => {
    load();
  }, [load, path]);

  const save = useCallback(
    async (raw: string) => {
      if (!path) return;
      await ds.saveDoc(path, raw);
      load();
    },
    [path, ds, load],
  );

  const commit = useCallback(
    async (message?: string) => {
      if (!path) return;
      await ds.commitDoc([path], message);
    },
    [path, ds],
  );

  return { doc, loading, error, reload: load, save, commit };
}
