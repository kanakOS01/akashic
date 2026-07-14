import { parse } from "yaml";

export function parseFrontmatter(raw: string): { data: Record<string, unknown>; content: string } {
  const match = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/.exec(raw);
  if (!match) {
    return { data: {}, content: raw };
  }
  try {
    const data = parse(match[1]) as Record<string, unknown>;
    return { data: data ?? {}, content: match[2] };
  } catch {
    return { data: {}, content: match[2] };
  }
}
