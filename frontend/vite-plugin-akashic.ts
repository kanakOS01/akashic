import type { Connect, Plugin, ViteDevServer } from "vite";
import { existsSync, statSync } from "node:fs";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join, relative, resolve } from "node:path";
import { realpath } from "node:fs/promises";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import type { ServerResponse } from "node:http";

const execFileAsync = promisify(execFile);

const SECTION_ORDER = [
  "services",
  "flows",
  "system",
  "entities",
  "adr",
  "glossary",
] as const;

const FRONTMATTER_TYPES: Record<string, string> = {
  services: "service",
  flows: "flow",
  system: "system",
  entities: "entity",
  adr: "adr",
  glossary: "glossary",
};

interface Frontmatter {
  title?: string;
  type?: string;
  summary?: string;
  description?: string;
  [key: string]: unknown;
}

interface NavItem {
  path: string;
  title: string;
  type: string;
}

interface NavSection {
  id: string;
  title: string;
  items: NavItem[];
}

interface IndexEntry {
  path: string;
  title: string;
  section: string;
  type: string;
  summary: string;
  tags: string[];
  updated: string;
}

interface NavTree {
  home: string;
  sections: NavSection[];
  index: IndexEntry[];
}

interface DocRecord {
  path: string;
  title: string;
  type: string;
  frontmatter: Frontmatter;
  content: string;
  raw: string;
}

interface Snapshot {
  mode: "static";
  home: string;
  sections: NavSection[];
  index: IndexEntry[];
  docs: Record<string, DocRecord>;
}

export function parseFrontmatter(raw: string): { data: Frontmatter; content: string } {
  const match = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/.exec(raw);
  if (!match) {
    return { data: {}, content: raw };
  }
  let data: Frontmatter = {};
  try {
    // Lazily avoid a hard dependency on yaml at the plugin level.
    const yaml = match[1];
    for (const line of yaml.split(/\r?\n/)) {
      const kv = /^([A-Za-z0-9_-]+):\s*(.*)$/.exec(line);
      if (kv) {
        const value = kv[2].trim();
        data[kv[1]] = value;
      }
    }
  } catch {
    data = {};
  }
  return { data, content: match[2] };
}

async function resolveSafe(root: string, rel: string): Promise<string> {
  const cleaned = rel.replace(/^\/+/, "");
  const abs = resolve(root, cleaned);
  const realRoot = await realpath(root);
  const realAbs = (await existsSafe(abs)) ? await realpath(abs) : abs;
  if (realAbs !== realRoot && !realAbs.startsWith(realRoot + "/")) {
    throw new Error("Path escapes knowledge root");
  }
  return abs;
}

async function existsSafe(p: string): Promise<boolean> {
  try {
    await realpath(p);
    return true;
  } catch {
    return false;
  }
}

function sectionFromPath(root: string, absPath: string): string {
  const rel = relative(root, absPath).split(/[\\/]/)[0] ?? "";
  return rel;
}

function inferTitle(data: Frontmatter, root: string, absPath: string): string {
  if (data.title) return String(data.title);
  const rel = relative(root, absPath).split(/[\\/]/).join("/").replace(/\.md$/, "");
  const name = rel.includes("/") ? rel.split("/").slice(1).join("/") : rel;
  return name.replace(/[-_]/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function inferType(data: Frontmatter, root: string, absPath: string): string {
  if (data.type) return String(data.type);
  const section = sectionFromPath(root, absPath);
  return FRONTMATTER_TYPES[section] ?? section;
}

async function readDoc(root: string, rel: string): Promise<DocRecord> {
  const abs = await resolveSafe(root, rel);
  if (!existsSync(abs)) {
    throw Object.assign(new Error("Not found"), { status: 404 });
  }
  const raw = await readFile(abs, "utf8");
  const { data, content } = parseFrontmatter(raw);
  const title = inferTitle(data, root, abs);
  const type = inferType(data, root, abs);
  return { path: rel, title, type, frontmatter: data, content, raw };
}

async function readAllDocs(root: string): Promise<DocRecord[]> {
  const out: DocRecord[] = [];
  const readDir = async (dir: string): Promise<void> => {
    const fs = await import("node:fs");
    const entries = await fs.promises.readdir(dir, { withFileTypes: true });
    for (const entry of entries) {
      const full = join(dir, entry.name);
      if (entry.isDirectory()) {
        if (entry.name === ".git" || entry.name === ".akashic" || entry.name === "node_modules") continue;
        await readDir(full);
      } else if (entry.isFile() && entry.name.endsWith(".md")) {
        const rel = relative(root, full).split(/[\\/]/).join("/");
        try {
          out.push(await readDoc(root, rel));
        } catch {
          // skip unreadable
        }
      }
    }
  };
  await readDir(root);
  return out;
}

async function buildNav(root: string): Promise<NavTree> {
  const docs = await readAllDocs(root);
  const sections: NavSection[] = [];
  const index: IndexEntry[] = [];

  const homeDoc = docs.find((d) => d.path === "README.md");
  const home = homeDoc ? "README.md" : docs[0]?.path ?? "README.md";

  const bySection = new Map<string, DocRecord[]>();
  for (const doc of docs) {
    if (doc.path === "README.md") continue;
    const section = sectionFromPath(root, join(root, doc.path));
    if (!section) continue;
    const list = bySection.get(section) ?? [];
    list.push(doc);
    bySection.set(section, list);
  }

  for (const id of SECTION_ORDER) {
    const list = (bySection.get(id) ?? []).sort((a, b) => a.title.localeCompare(b.title));
    if (list.length === 0) continue;
    sections.push({
      id,
      title: id.charAt(0).toUpperCase() + id.slice(1),
      items: list.map((d) => ({ path: d.path, title: d.title, type: d.type })),
    });
    for (const d of list) {
      index.push({
        path: d.path,
        title: d.title,
        section: id,
        type: d.type,
        summary: typeof d.frontmatter.summary === "string"
          ? d.frontmatter.summary
          : typeof d.frontmatter.description === "string"
            ? d.frontmatter.description
            : firstParagraph(d.content),
        tags: [],
        updated: fileUpdated(d.path, root),
      });
    }
  }

  return { home, sections, index };
}

function firstParagraph(content: string): string {
  const text = content.replace(/<!--[\s\S]*?-->/g, "").trim();
  const match = /^[^\n#]+/.exec(text);
  const para = match ? match[0].trim() : "";
  return para.length > 200 ? para.slice(0, 200) + "…" : para;
}

function fileUpdated(rel: string, root: string): string {
  try {
    const stat = statSync(join(root, rel));
    return stat.mtime.toISOString();
  } catch {
    return "";
  }
}

async function writeDoc(root: string, rel: string, raw: string): Promise<string> {
  const abs = await resolveSafe(root, rel);
  await mkdir(dirname(abs), { recursive: true });
  await writeFile(abs, raw, "utf8");
  return new Date().toISOString();
}

async function commitDocs(root: string, paths: string[], message?: string): Promise<void> {
  const absPaths = await Promise.all(paths.map((p) => resolveSafe(root, p)));
  await execFileAsync("git", ["-C", root, "add", ...absPaths]);
  const msg = message || `docs: update ${paths.length} file(s) via Akashic site`;
  try {
    await execFileAsync("git", ["-C", root, "commit", "-m", msg]);
  } catch (err) {
    const e = err as { stderr?: string; stdout?: string };
    const out = (e.stderr || e.stdout || "").trim();
    if (/nothing to commit/i.test(out)) {
      throw Object.assign(new Error("Nothing to commit"), { status: 409 });
    }
    throw err;
  }
}

function sendJson(res: ServerResponse, status: number, body: unknown): void {
  const payload = JSON.stringify(body);
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json");
  res.end(payload);
}

function readBody(req: Connect.IncomingMessage): Promise<string> {
  return new Promise((resolve, reject) => {
    let data = "";
    req.on("data", (chunk) => (data += chunk));
    req.on("end", () => resolve(data));
    req.on("error", reject);
  });
}

export async function buildSnapshot(root: string): Promise<Snapshot> {
  const nav = await buildNav(root);
  const docs: Record<string, DocRecord> = {};
  for (const entry of nav.index) {
    try {
      docs[entry.path] = await readDoc(root, entry.path);
    } catch {
      // skip
    }
  }
  if (nav.home && !docs[nav.home]) {
    try {
      docs[nav.home] = await readDoc(root, nav.home);
    } catch {
      // skip
    }
  }
  return { mode: "static", home: nav.home, sections: nav.sections, index: nav.index, docs };
}

export function akashicPlugin(kbRootRaw: string): Plugin {
  const buildMode = process.env.NODE_ENV === "production" && Boolean(process.env.AKASHIC_DIST_DIR);

  return {
    name: "akashic-knowledge",
    configureServer(server: ViteDevServer) {
      const root = resolve(kbRootRaw);
      const handler: Connect.NextHandleFunction = async (req, res, next) => {
        try {
          const url = new URL(req.url ?? "/", "http://localhost");
          const route = url.pathname;

          if (route === "/meta" && req.method === "GET") {
            let gitAvailable = false;
            try {
              await execFileAsync("git", ["-C", root, "rev-parse", "--is-inside-work-tree"]);
              gitAvailable = true;
            } catch {
              gitAvailable = false;
            }
            return sendJson(res, 200, {
              mode: "live",
              editable: true,
              gitAvailable,
              kbRoot: root,
              port: server.config.server.port,
            });
          }

          if (route === "/nav" && req.method === "GET") {
            const nav = await buildNav(root);
            return sendJson(res, 200, nav);
          }

          if (route === "/doc" && req.method === "GET") {
            const path = url.searchParams.get("path") ?? "";
            try {
              const doc = await readDoc(root, path);
              return sendJson(res, 200, doc);
            } catch (err) {
              const status = (err as { status?: number }).status ?? 500;
              return sendJson(res, status, { error: (err as Error).message });
            }
          }

          if (route === "/doc" && req.method === "PUT") {
            const body = JSON.parse(await readBody(req)) as { path: string; raw: string };
            try {
              const updated = await writeDoc(root, body.path, body.raw);
              return sendJson(res, 200, { path: body.path, updated });
            } catch (err) {
              const status = (err as { status?: number }).status ?? 500;
              return sendJson(res, status, { error: (err as Error).message });
            }
          }

          if (route === "/commit" && req.method === "POST") {
            const body = JSON.parse(await readBody(req)) as { paths: string[]; message?: string };
            try {
              await commitDocs(root, body.paths, body.message);
              return sendJson(res, 200, { commit: "ok" });
            } catch (err) {
              const status = (err as { status?: number }).status ?? 500;
              return sendJson(res, status, { error: (err as Error).message });
            }
          }

          next();
        } catch (err) {
          sendJson(res, 500, { error: (err as Error).message });
        }
      };
      server.middlewares.use("/api", handler);
    },
    resolveId(id) {
      if (id === "virtual:akashic-snapshot") return "\0akashic-snapshot";
      return null;
    },
    async load(id) {
      if (id === "\0akashic-snapshot") {
        if (buildMode) {
          const snapshot = await buildSnapshot(resolve(kbRootRaw));
          return `export default ${JSON.stringify(snapshot)};`;
        }
        return `export default null;`;
      }
      return null;
    },
  };
}

export default akashicPlugin;
