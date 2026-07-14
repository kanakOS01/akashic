import { useEffect, useState } from "react";
import { createDataSource } from "../lib/dataSource";
import type { Meta } from "../lib/types";

const ds = createDataSource();

export function useMeta() {
  const [meta, setMeta] = useState<Meta | null>(null);
  useEffect(() => {
    let active = true;
    ds.getMeta()
      .then((m) => active && setMeta(m))
      .catch(() => active && setMeta({ mode: ds.mode, editable: ds.editable, gitAvailable: ds.gitAvailable, kbRoot: "", port: 0 }));
    return () => {
      active = false;
    };
  }, []);
  return meta;
}

export { ds };
