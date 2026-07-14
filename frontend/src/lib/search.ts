import { useMemo } from "react";
import MiniSearch from "minisearch";
import type { DocRecord, IndexEntry } from "./types";

export function useSearch(index: IndexEntry[], docs: Record<string, DocRecord>) {
  const mini = useMemo(() => {
    const engine = new MiniSearch<IndexEntry>({
      fields: ["title", "summary", "section"],
      storeFields: ["path", "title", "section", "type", "summary"],
      searchOptions: { boost: { title: 2 }, prefix: true, fuzzy: 0.2 },
    });
    engine.addAll(index);
    return engine;
  }, [index]);

  const search = useMemo(() => {
    return (query: string): IndexEntry[] => {
      const q = query.trim();
      if (!q) return [];
      const results = mini.search(q).map((r) => ({
        path: r.path as string,
        title: r.title as string,
        section: r.section as string,
        type: r.type as string,
        summary: r.summary as string,
        tags: [],
        updated: "",
      }));
      void docs;
      return results;
    };
  }, [mini, docs]);

  return { search };
}
