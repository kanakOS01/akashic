import snapshot from "virtual:akashic-snapshot";
import type { DocRecord, Meta, NavTree, Snapshot } from "./types";

export interface DataSource {
  readonly mode: "live" | "static";
  readonly editable: boolean;
  readonly gitAvailable: boolean;
  getMeta(): Promise<Meta>;
  getNav(): Promise<NavTree>;
  getDoc(path: string): Promise<DocRecord>;
  saveDoc(path: string, raw: string): Promise<{ path: string; updated: string }>;
  commitDoc(paths: string[], message?: string): Promise<void>;
}

class LiveApiDataSource implements DataSource {
  readonly mode = "live" as const;
  readonly editable = true;
  readonly gitAvailable = true;

  async getMeta(): Promise<Meta> {
    const res = await fetch("/api/meta");
    return res.json();
  }

  async getNav(): Promise<NavTree> {
    const res = await fetch("/api/nav");
    return res.json();
  }

  async getDoc(path: string): Promise<DocRecord> {
    const res = await fetch(`/api/doc?path=${encodeURIComponent(path)}`);
    if (!res.ok) throw new Error(await errorText(res));
    return res.json();
  }

  async saveDoc(path: string, raw: string): Promise<{ path: string; updated: string }> {
    const res = await fetch("/api/doc", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path, raw }),
    });
    if (!res.ok) throw new Error(await errorText(res));
    return res.json();
  }

  async commitDoc(paths: string[], message?: string): Promise<void> {
    const res = await fetch("/api/commit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ paths, message }),
    });
    if (!res.ok) throw new Error(await errorText(res));
  }
}

class StaticSnapshotDataSource implements DataSource {
  readonly mode = "static" as const;
  readonly editable = false;
  readonly gitAvailable = false;
  private snapshot: Snapshot;

  constructor(snapshot: Snapshot) {
    this.snapshot = snapshot;
  }

  async getMeta(): Promise<Meta> {
    return {
      mode: "static",
      editable: false,
      gitAvailable: false,
      kbRoot: "",
      port: 0,
    };
  }

  async getNav(): Promise<NavTree> {
    return { home: this.snapshot.home, sections: this.snapshot.sections, index: this.snapshot.index };
  }

  async getDoc(path: string): Promise<DocRecord> {
    const doc = this.snapshot.docs[path];
    if (!doc) throw new Error(`Document not found: ${path}`);
    return doc;
  }

  async saveDoc(): Promise<{ path: string; updated: string }> {
    throw new Error("Editing is disabled in the static site.");
  }

  async commitDoc(): Promise<void> {
    throw new Error("Committing is disabled in the static site.");
  }
}

async function errorText(res: Response): Promise<string> {
  try {
    const body = await res.json();
    return body.error ?? res.statusText;
  } catch {
    return res.statusText;
  }
}

export function createDataSource(): DataSource {
  if (snapshot) {
    return new StaticSnapshotDataSource(snapshot);
  }
  return new LiveApiDataSource();
}
